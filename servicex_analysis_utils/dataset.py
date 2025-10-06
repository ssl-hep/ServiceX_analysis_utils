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
    ds_name: str
) -> Union[dataset.FileList, dataset.Rucio, dataset.XRootD]:
    """Determine the type of dataset based on the input
    string and then return the ServiceX dataset object.

    Args:
        ds_name (str): Name of the dataset to fetch.

    Returns:
        Tuple[dataset type]: The dataset object
    """
    what_is_it = None

    if re.match(r"^https?://", ds_name):
        what_is_it = "url"
        url = ds_name

        parsed_url = urlparse(url)
        if "cernbox.cern.ch" in parsed_url.netloc and parsed_url.path.startswith(
            "/files/spaces"
        ):
            remote_file = f"root://eospublic.cern.ch{parsed_url.path[13:]}"
            what_is_it = "remote_file"

    elif re.match(r"^rucio://", ds_name):
        what_is_it = "rucio"
        did = ds_name[8:]

    else:
        did = ds_name
        what_is_it = "rucio"

    if what_is_it == "url":
        return dataset.FileList([url])

    if what_is_it == "remote_file":
        return dataset.FileList([remote_file])

    if what_is_it == "rucio":
        return dataset.Rucio(did)

    raise RuntimeError(f"Unknown input type: {what_is_it}")