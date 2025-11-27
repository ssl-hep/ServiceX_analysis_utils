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
import pytest
from servicex_analysis_utils import ds_type_resolver
from servicex import dataset


@pytest.mark.parametrize(
    "input_ds, expected_type",
    [
        ("https://test.com", dataset.FileList),
        ("test:data", dataset.Rucio),
        ("rucio://test:test", dataset.Rucio),
        ("123", dataset.CERNOpenData),
        (123, dataset.CERNOpenData),
        ("root://eosatlas.cern.ch//eos/", dataset.FileList),
        ("root://eosatlas.cern.ch//eos/*", dataset.XRootD),
        (["root://eosatlas.cern.ch//eos/", "https://test.com"], dataset.FileList),
        ("mc20_13TeV_valid_dataset_name", dataset.Rucio),
        ("data22_13p6TeV_valid_dataset_name", dataset.Rucio),
    ],
)
def test_find_dataset(input_ds, expected_type):
    dataset = ds_type_resolver(input_ds)
    assert isinstance(dataset, expected_type)


@pytest.mark.parametrize(
    "eos_path, prefix",
    [
        ("/eos/opendata/atlas/rucio/somefile.root", "root://eospublic.cern.ch/"),
        ("/eos/opendata/cms/rucio/somefile.root", "root://eospublic.cern.ch/"),
        ("/eos/atlas/atlascerngroupdisk/somefile.root", "root://eosatlas.cern.ch/"),
        ("/eos/cms/store/somefile.root", "root://eoscms.cern.ch/"),
    ],
)
def test_eos_url_parsing(eos_path, prefix):
    ds_out = ds_type_resolver(eos_path)
    assert isinstance(ds_out, dataset.FileList)
    assert ds_out.files[0] == prefix + eos_path
