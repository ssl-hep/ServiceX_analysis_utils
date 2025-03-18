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

import servicex
import uproot

def run_query(input_filenames=None):
    import uproot
    import awkward as ak
    """
    Helper. Open a file and return one array containing a single string that describes the DataSet root file structure.
    Sent to ServiceX python transformers.

    The string will be formatted like:
    "Tree: TreeName1; TBranch: Branchname1 ; dtype: BranchType1, TBranch: Branchname2 ; dtype: BranchType2, ...
     Tree: TreeName2; TBranch: Branchname1 ; dtype: BranchType1, ..."
    """
    def is_tree(obj):
        """
        Helper to check if a root file item is TTree. Different object types use .classname or .classnames
        """
        # Check for 'classname'
        if hasattr(obj, "classname"):
            cls_attr = obj.classname
            # Call if it's callable
            cls_value = cls_attr() if callable(cls_attr) else cls_attr
            return "TTree" in cls_value
        # Check for 'classnames'
        elif hasattr(obj, "classnames"):
            cls_attr = obj.classnames
            cls_values = cls_attr() if callable(cls_attr) else cls_attr
            return any("TTree" in cls for cls in cls_values)
        return False
        
    trees_info = []  #  list of str info for each tree

    with uproot.open(input_filenames) as file:
        for tree_name in file.keys():
            # Remove uproot tree sufix
            tree_name_clean = tree_name.rstrip(";1")
            tree = file[tree_name]

            # Only TTrees
            if not is_tree(tree):
                continue

            # Gather branch info
            branch_info_list = []
            for branch_name, branch in tree.items():
                # Using uproot type interpretor
                branch_type = str(branch.interpretation)
                branch_info_list.append(f"TBranch: {branch_name} ; dtype: {branch_type}")

            # Join branch info & separate by ,
            tree_info = f"Tree: {tree_name_clean}; " + ", ".join(branch_info_list)
            trees_info.append(tree_info)

    # Join all trees & separate by \n
    final_str = "\n".join(trees_info)
    
    # Return str in an array
    return ak.Array([final_str])

def print_structure_from_str(deliver_dict, filter_branch="", save_to_txt=False, do_print=False):
    """
    Converts dataset file structures to a formatted string.

    Parameters:
      deliver_dict (dict): ServiceX deliver output (keys: sample names, values: file paths or URLs).
      filter_branch (str): If provided, only branches containing this string are included.
      save_to_txt (bool): If True, saves output to a text file instead of returning it.

    Returns:
      str: The formatted file structure.
    """
    output_lines = []
    output_lines.append(f"\nFile structure of all samples with branch filter '{filter_branch}':")

    for sample_name, path in deliver_dict.items():
        output_lines.append(
            f"\n---------------------------\n"
            f"\U0001F4C1 Sample: {sample_name}\n"
            f"---------------------------"
        )

        with uproot.open(path[0]) as f:
            structure_str = f["servicex"]["branch"].array()[0]

        tree_lines = structure_str.split("\n")
        for line in tree_lines:
            if not line.strip():
                continue  # Skip empty lines
            
            parts = line.split(";", 1)
            tree_header = parts[0]
            output_lines.append(f"\n\U0001F333 {tree_header}")

            if len(parts) > 1:
                branch_infos = parts[1].split(",")
                output_lines.append("   ├── Branches:")
                for b in branch_infos:
                    branch_line = b.strip()
                    if filter_branch not in branch_line:
                        continue
                    if branch_line.startswith("TBranch:"):
                        output_lines.append(f"   │   ├── {branch_line[8:]}")
    
    result_str = "\n".join(output_lines)

    if save_to_txt:
        with open("samples_structure.txt", "w") as f:
            f.write(result_str)
        return "File structure saved to 'samples_structure.txt'."
    if do_print:
        print(result_str)
        return 
    else:
        return result_str

def build_deliver_spec(dataset):
    #Servicex query using the PythonFunction backend
    query_PythonFunction = servicex.query.PythonFunction().with_uproot_function(run_query)
    
    #Create a dict with sample name for ServiceX query & datasetID
    dataset_dict={}
    user_in=type(dataset)
    
    if user_in == str:
        dataset_dict.update({"Sample":dataset})
    elif user_in == list and type(dataset[0]) is str:
        for i in range(len(dataset)):
            name="Sample"+str(i+1) #write number for humans
            dataset_dict.update({name:dataset[i]})
    elif user_in == dict:
        dataset_dict=dataset
    else:
        raise ValueError(f"Unsupported dataset input type: {user_in}.\nInput must be dict ('sample_name':'dataset_id'), str or list of str")
    
    sample_list = [
        {
            "NFiles": 1,
            "Name": name,
            "Dataset": servicex.dataset.Rucio(did),
            "Query": query_PythonFunction,
        }
        for name, did in dataset_dict.items()
    ]
    spec_python = {"Sample": sample_list}

    return spec_python
    

def get_structure(dataset, **kwargs):
    """
    Utility function. 
    Creates and sends the ServiceX request from user inputed datasets to retrieve file stucture.
    Calls print_structure_from_str()

    Parameters:
      dataset (dict,str,[str]): The datasets from which to print the file structures.
                                A custom sample name per dataset can be given in a dict form: {'sample_name':'dataset_id'}
      kwargs : Arguments to be propagated to print_structure_from_str 
    """
    spec_python=build_deliver_spec(dataset)

    output=servicex.deliver(spec_python)

    return print_structure_from_str(output, **kwargs)