import awkward as ak
import numpy as np

def parse_jagged_depth_and_dtype(dtype_str):
    """
    Helper to decode the dtype str for each branch.

    Parses uproot-style interpretation strings such as:
    - "AsJagged(AsJagged(AsDtype('>f4')))"

    Returns the number of nested AsJagged(...) layers 
    and the inner dtype string to be used with np.dtype

    Parameters:
        dtype_str (str): A string representing the uproot interpretation of a branch.

    Returns:
        Tuple[int, Optional[str]]: (jagged_depth, base_numpy_dtype_str) or None if not recognized.
    """
    depth = 0
    current = dtype_str.strip()

    # Count how many nested AsJagged(...) wrappers exist
    while current.startswith("AsJagged("):
        depth += 1
        current = current[len("AsJagged("):-1].strip()  # Strip outermost wrapper, up to -1 to remove )

    # Extract the base dtype string from AsDtype('<np-format>')
    if current.startswith("AsDtype('") and current.endswith("')"):
        base_dtype = current[len("AsDtype('"):-2]
        return depth, base_dtype
    else:
        return depth, None

def decode_ak_array(encoded_str):
    """
    Helper
    Decodes the structured string and reconstructs ak.Arrays
    mimicking TTrees with correct field names and dtypes. 
    Decoded ak types are translated from uproot.interpretation and 
    recreate the nested AsJagged(AsJagged(...)) arrays.

    Parameters:
        encoded_str (str): The encoded string from run_query.

    Returns:
        dict[str, ak.Array]: Dictionary where keys are tree names and values are ak.Arrays with the correct structure.
    """

    tree_sections = encoded_str.strip().split("\n")
    reconstructed_data = {}

    for tree_section in tree_sections:
        tree_section = tree_section.strip()
        if not tree_section:
            continue

        parts = tree_section.split(";", 1)
        tree_header = parts[0].strip()

        # Simple manual slicing to extract tree name
        treename = tree_header[len("Tree: "):]
        branches = {}

        if len(parts) > 1:
            branches_str = parts[1].strip()
            branch_infos = branches_str.split(",")

            for branch in branch_infos:
                branch = branch.strip()

                if " ; dtype: " in branch:  # line with branch info
                    name_str, dtype_str = branch.split(" ; dtype: ", 1)
                    branch_name = name_str.replace("TBranch: ", "").strip()
                    dtype_str = dtype_str.strip()

                    # Determine nesting depth and base dtype from interpretation string
                    depth, base_dtype_str = parse_jagged_depth_and_dtype(dtype_str)
                    if base_dtype_str is None:
                        branches[branch_name] = None
                        continue

                    try:
                        np_dtype = np.dtype(base_dtype_str)
                    except TypeError:
                        branches[branch_name] = None
                        continue

                    dummy = np.zeros(1, dtype=np_dtype)[0]  # Typed placeholder value

                    # Simulate jagged structure by nesting the value in lists
                    for _ in range(depth):
                        dummy = [dummy]  # one level of jaggedness

                    # Wrap dummy in a length-1 ak.Array
                    branches[branch_name] = ak.Array([dummy])

        if branches:
            # Each tree becomes a record array with 1 entry (dict of branch arrays)
            reconstructed_data[treename] = ak.Array([branches])

    return reconstructed_data

# Test input with multiple trees, varied nesting and types including a string
encoded_str = (
    "Tree: testTree1; "
    "TBranch: a ; dtype: AsDtype('>f4'), "
    "TBranch: b ; dtype: AsJagged(AsDtype('>i4'))\n"
    "Tree: testTree2; "
    "TBranch: x ; dtype: AsJagged(AsJagged(AsDtype('>u4'))), "
    "TBranch: y ; dtype: AsDtype('>f8'), "
    "TBranch: label ; dtype: AsDtype('>S10')"
)

result = decode_ak_array(encoded_str)
for tree, array in result.items():
    print(f"\nTree: {tree}")
    #print(array)
    print(array.type)
