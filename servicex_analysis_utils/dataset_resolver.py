# Copyright (c) 2025, IRIS-HEP
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import re
from typing import Union
from urllib.parse import urlparse

from servicex import dataset


def ds_type_resolver(
    ds_name: Union[str, list[str]],
) -> Union[dataset.FileList, dataset.Rucio, dataset.XRootD, dataset.CERNOpenData]:
    """Determine the type of dataset based on the input
    string and then return the ServiceX dataset object.

    Args:
        ds_name (str): Name of the dataset to fetch.

    Returns:
        dataset: The dataset object
    """

    if isinstance(ds_name, list):
        return dataset.FileList(ds_name)

    elif re.match(r"^https?://", ds_name):
        url = ds_name

        parsed_url = urlparse(url)
        if "cernbox.cern.ch" in parsed_url.netloc and parsed_url.path.startswith(
            "/files/spaces"
        ):
            url = f"root://eospublic.cern.ch{parsed_url.path[13:]}"

        return dataset.FileList([url])

    elif re.match(r"^rucio://", ds_name):
        did = ds_name[8:]
        return dataset.Rucio(did)

    elif ds_name.count(":") == 1 and "/" not in ds_name:
        return dataset.Rucio(ds_name)

    elif ds_name.isdigit():
        return dataset.CERNOpenData(int(ds_name))

    elif ds_name.startswith("root://") and ds_name.endswith("*"):
        return dataset.XRootD(ds_name)

    elif re.match(r"^root://", ds_name):
        return dataset.FileList(ds_name)

    raise RuntimeError(
        f"Unable to find the type of input provided for dataset: {ds_name}"
    )
