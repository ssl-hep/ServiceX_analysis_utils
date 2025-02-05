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
import os
import sys
import numpy as np

#Setting rpath
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from servicex_analysis_utils.materialization import to_awk

def build_test_samples():
    # example data for two branches
    tree_data1 = {
    "branch1": np.ones(100),
    "branch2": np.zeros(100)
    }
    # example data for one branch
    tree_data2 = {"branch1": np.ones(10)}  

    # Create tmp .root files
    with uproot.create(test_path1) as file:
        file["Tree"] = tree_data1
    
    with uproot.create(test_path2) as file:
        file["Tree"] = tree_data2

#Initial test configuration
@pytest.fixture(scope="function", autouse=True)
def init(tmp_path):
    #Setting global variables to be used in the tests and helper function
    global test_path1, test_path2, \
           result, result_da, result_filtered 

    test_path1 = tmp_path / "test_file1.root"
    test_path2 = tmp_path / "test_file2.root"

    #Building dumy test files
    if not os.path.exists(test_path1) or not os.path.exists(test_path2):
        build_test_samples()

    #Dict like servicex.deliver() output
    sx_dict = {"Test-Sample1": test_path1, "Test-Sample2": test_path2}

    #Executing to_awk() and saving results for tests
    result = to_awk(sx_dict)
    result_da = to_awk(sx_dict, dask=True, step_size=10) #uproot.dask step_size kwarg
    result_filtered = to_awk(sx_dict, expressions="branch1") #uproot.iterate expressions kwarg

#Test functions
def test_to_awk_instances():
    arr1=result["Test-Sample1"]
    da_arr1=result_da["Test-Sample1"]

    #Testing returned types
    assert isinstance(arr1, ak.Array), "to_awk() does not produce an awkward.Array instance"
    assert isinstance(da_arr1, dak.Array), "to_awk(dask=True) does not produce a dask_awkward.Array instance"

def test_to_awk_collection():
    arr1=result["Test-Sample1"]
    arr2=result["Test-Sample2"]

    #Collecting all samples 
    assert list(result.keys())==["Test-Sample1", "Test-Sample2"]

    #Collecting all branches
    assert ak.fields(arr1) == ['branch1', 'branch2']
    assert ak.fields(arr2) == ['branch1']

    #Collecting all elements per branch
    assert ak.all(arr1['branch2'] == ak.from_numpy(np.zeros(100)))
    assert ak.all(arr2['branch1'] == ak.from_numpy(np.ones(10)))

def test_to_awk_dask():
    arr1=result_da["Test-Sample1"]
    arr2=result_da["Test-Sample2"]

    #Testing if dask.compute() leads to same results
    assert ak.almost_equal(arr1.compute(), result["Test-Sample1"])
    assert ak.almost_equal(arr2.compute(), result["Test-Sample2"])

    #Testing partitionning kwarg
    assert arr1.npartitions == 10
    assert arr2.npartitions == 1

def test_to_awk_filter():
    arr1=result_filtered["Test-Sample1"]
    arr2=result_filtered["Test-Sample2"]

    #Testing if filtering kwargs are passed to uproot.iterate()
    assert ak.fields(arr1) == ['branch1'] #branch2 should be filtered out
    assert ak.fields(arr2) == ['branch1'] 





    

