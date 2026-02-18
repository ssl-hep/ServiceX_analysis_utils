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
import uproot
import awkward as ak
import dask_awkward as dak
import logging
import numpy as np
from servicex_analysis_utils import to_awk
import types


@pytest.fixture
def build_test_samples(tmp_path):

    test_path1 = str(tmp_path / "test_file1.root")
    test_path2 = str(tmp_path / "test_file2.root")
    # example data for two branches
    tree_data1 = {"branch1": np.ones(100), "branch2": np.zeros(100)}
    # example data for one branch
    tree_data2 = {"branch1": np.ones(10)}

    # Create tmp .root files
    with uproot.create(test_path1) as file:
        file["Tree"] = tree_data1

    with uproot.create(test_path2) as file:
        file["Tree"] = tree_data2

    # Dict like servicex.deliver() output
    sx_dict = {"Test-Sample1": [test_path1], "Test-Sample2": [test_path2]}

    return sx_dict


# Test functions
def test_to_awk(build_test_samples):
    sx_dict = build_test_samples
    result = to_awk(sx_dict)  # uproot.iterate expressions kwarg

    # Collecting all samples
    assert list(result.keys()) == ["Test-Sample1", "Test-Sample2"]
    arr1 = result["Test-Sample1"]
    arr2 = result["Test-Sample2"]

    # Collecting all branches
    assert ak.fields(arr1) == ["branch1", "branch2"]
    assert ak.fields(arr2) == ["branch1"]

    assert isinstance(
        arr1, ak.Array
    ), "to_awk() does not produce an awkward.Array instance"
    assert isinstance(
        arr2, ak.Array
    ), "to_awk() does not produce an awkward.Array instance"

    # Collecting all elements per branch
    assert ak.all(arr1["branch2"] == ak.from_numpy(np.zeros(100)))
    assert ak.all(arr2["branch1"] == ak.from_numpy(np.ones(10)))

    # Checking kwargs
    result_filtered = to_awk(
        sx_dict, expressions="branch1"
    )  # uproot.iterate expressions kwarg
    arr1_filtered = result_filtered["Test-Sample1"]
    assert ak.fields(arr1_filtered) == ["branch1"]  # branch2 should be filtered out


def test_to_awk_dask(build_test_samples):
    sx_dict = build_test_samples
    result_da = to_awk(sx_dict, dask=True, step_size=10)  # uproot.dask step_size kwarg

    # Collecting all samples
    assert list(result_da.keys()) == ["Test-Sample1", "Test-Sample2"]
    arr1 = result_da["Test-Sample1"]
    arr2 = result_da["Test-Sample2"]

    # Checking instance
    assert isinstance(
        arr1, dak.Array
    ), "to_awk(dask=True) does not produce an dak.Array instance"
    assert isinstance(
        arr2, dak.Array
    ), "to_awk(dask=True) does not produce an dak.Array instance"

    # Testing partitionning kwarg
    assert arr1.npartitions == 10
    assert arr2.npartitions == 1

    # Collecting all branches
    assert ak.fields(arr1) == ["branch1", "branch2"]
    assert ak.fields(arr2) == ["branch1"]

    # Collecting all elements per branch
    assert ak.all(arr1["branch2"].compute() == ak.from_numpy(np.zeros(100)))
    assert ak.all(arr2["branch1"].compute() == ak.from_numpy(np.ones(10)))


def test_to_awk_delayed_and_kwargs(build_test_samples):
    sx_dict = build_test_samples
    result_delay = to_awk(
        sx_dict, return_iterator=True, expressions="branch1"
    )  # return iterable + selection kwarg

    # Checking iterator return type
    assert isinstance(result_delay["Test-Sample1"], types.GeneratorType)
    assert isinstance(result_delay["Test-Sample2"], types.GeneratorType)

    arr1 = ak.concatenate(
        list(result_delay["Test-Sample1"])
    )  # Materialize the generator from uproot.iterate
    arr2 = ak.concatenate(list(result_delay["Test-Sample2"]))

    # Checking materialization
    assert isinstance(
        arr1, ak.Array
    ), "to_awk(dask=True) does not produce an ak.Array instance"
    assert isinstance(
        arr2, ak.Array
    ), "to_awk(dask=True) does not produce an ak.Array instance"

    # Checking only 1 branch selected
    assert ak.fields(arr1) == ["branch1"]
    assert ak.fields(arr2) == ["branch1"]


def test_unsupported_file_format():
    fake_paths = {"fake-Sample": ["invalid_file.txt"]}
    # match is regex-level
    with pytest.raises(
        RuntimeError,
        match=r"Unsupported delivered format: 'invalid_file\.txt'\. Must be \.root or Parquet \(\.parquet, \.pq\)",
    ):
        to_awk(fake_paths)


def test_empty_deliver_dict():
    empty_dict = {}
    with pytest.raises(
        RuntimeError, match="Input dict from servicex.deliver cannot be empty."
    ):
        to_awk(empty_dict)


def test_deliver_dict_empty_paths():
    empty_dict = {"empty-Sample": []}
    with pytest.raises(
        RuntimeError,
        match="Delivered result file path list for empty-Sample is empty.",
    ):
        to_awk(empty_dict)


@pytest.fixture
def build_test_samples_empty_file(tmp_path):
    test_path1 = str(tmp_path / "test_file1.root")
    # example data for two branches
    tree_data1 = {"branch1": np.array([]), "branch2": np.array([])}

    # Create tmp .root files
    with uproot.create(test_path1) as file:
        file["Tree"] = tree_data1

    # Dict like servicex.deliver() output
    sx_dict = {"Test-Sample1": [test_path1]}
    return sx_dict


def test_empty_file_warning(build_test_samples_empty_file, caplog):
    sx_dict = build_test_samples_empty_file
    # test logging warning
    with caplog.at_level(logging.WARNING):
        result = to_awk(sx_dict)

    # assert warning message
    assert (
        "Sample Test-Sample1 has no data to load. Returning empty array." in caplog.text
    )
    # assert is array
    assert isinstance(result["Test-Sample1"], ak.Array)
    # assert array is empty
    assert len(result["Test-Sample1"]) == 0
