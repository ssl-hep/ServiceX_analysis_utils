# Copyright (c) 2025, IRIS-HEP
# All rights reserved.
import pytest
import awkward as ak
import dask_awkward as dak
import logging
import numpy as np
import pyarrow.parquet as pq
from servicex_analysis_utils.materialization import to_awk


@pytest.fixture
def build_test_samples(tmp_path):
    """
    Creates two Parquet files with sample data for testing.
    """
    test_path1 = str(tmp_path / "test_file1.parquet")
    test_path2 = str(tmp_path / "test_file2.parquet")

    # Example data for two branches
    data1 = ak.Array({
        "branch1": np.ones(100),
        "branch2": np.zeros(100)
    })
    
    # Example data for one branch
    data2 = ak.Array({
        "branch1": np.ones(10)
    })

    # Write to Parquet files
    ak.to_parquet(data1, test_path1)
    ak.to_parquet(data2, test_path2)

    # Dict simulating servicex.deliver() output
    sx_dict = {"Test-Sample1": [test_path1], "Test-Sample2": [test_path2]}

    return sx_dict


# Test function for to_awk with Parquet files
def test_to_awk_collection(build_test_samples):
    sx_dict = build_test_samples
    result = to_awk(sx_dict)  # Using ak.from_parquet internally

    # Collecting all samples
    assert list(result.keys()) == ["Test-Sample1", "Test-Sample2"]
    arr1 = result["Test-Sample1"]
    arr2 = result["Test-Sample2"]

    # Collecting all branches
    assert ak.fields(arr1) == ['branch1', 'branch2']
    assert ak.fields(arr2) == ['branch1']

    assert isinstance(arr1, ak.Array), "to_awk() does not produce an awkward.Array instance"
    assert isinstance(arr2, ak.Array), "to_awk() does not produce an awkward.Array instance"

    # Collecting all elements per branch
    assert ak.all(arr1['branch2'] == ak.from_numpy(np.zeros(100)))
    assert ak.all(arr2['branch1'] == ak.from_numpy(np.ones(10)))

    # Checking kwargs 
    result_filtered = to_awk(sx_dict, columns="branch1")  
    arr1_filtered = result_filtered["Test-Sample1"]
    assert ak.fields(arr1_filtered) == ['branch1']  # branch2 should be filtered out
