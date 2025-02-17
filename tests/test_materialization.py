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
from servicex_analysis_utils.materialization import to_awk


@pytest.fixture
def build_test_samples(tmp_path):

    test_path1 = str(tmp_path / "test_file1.root")
    test_path2 = str(tmp_path / "test_file2.root")
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

    #Dict like servicex.deliver() output
    sx_dict = {"Test-Sample1": [test_path1], "Test-Sample2": [test_path2]}

    return sx_dict


#Test functions
def test_to_awk_collection(build_test_samples):
    sx_dict = build_test_samples
    result = to_awk(sx_dict) #uproot.iterate expressions kwarg

    #Collecting all samples 
    assert list(result.keys())==["Test-Sample1", "Test-Sample2"]
    arr1=result["Test-Sample1"]
    arr2=result["Test-Sample2"]

    #Collecting all branches
    assert ak.fields(arr1) == ['branch1', 'branch2']
    assert ak.fields(arr2) == ['branch1']
    
    assert isinstance(arr1, ak.Array), "to_awk() does not produce an awkward.Array instance"
    assert isinstance(arr2, ak.Array), "to_awk() does not produce an awkward.Array instance"
  
    #Collecting all elements per branch
    assert ak.all(arr1['branch2'] == ak.from_numpy(np.zeros(100)))
    assert ak.all(arr2['branch1'] == ak.from_numpy(np.ones(10)))

    #Checking kwargs
    result_filtered = to_awk(sx_dict, expressions="branch1") #uproot.iterate expressions kwarg
    arr1_filtered=result_filtered["Test-Sample1"]
    assert ak.fields(arr1_filtered) == ['branch1'] #branch2 should be filtered out


def test_to_awk_dask(build_test_samples):
    sx_dict = build_test_samples
    result_da = to_awk(sx_dict, dask=True, step_size=10) #uproot.dask step_size kwarg
    
    #Collecting all samples 
    assert list(result_da.keys())==["Test-Sample1", "Test-Sample2"]
    arr1=result_da["Test-Sample1"]
    arr2=result_da["Test-Sample2"]

    #Checking instance
    assert isinstance(arr1, dak.Array), "to_awk(dask=True) does not produce an dak.Array instance"
    assert isinstance(arr2, dak.Array), "to_awk(dask=True) does not produce an dak.Array instance"

    #Testing partitionning kwarg
    assert arr1.npartitions == 10
    assert arr2.npartitions == 1

    #Collecting all branches
    assert ak.fields(arr1) == ['branch1', 'branch2']
    assert ak.fields(arr2) == ['branch1']

    #Collecting all elements per branch
    assert ak.all(arr1['branch2'].compute() == ak.from_numpy(np.zeros(100)))
    assert ak.all(arr2['branch1'].compute() == ak.from_numpy(np.ones(10)))








    

