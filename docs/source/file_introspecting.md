# Remote File Introspecting

The `get_structure()` function allows users to query and inspect the internal structure of datasets available through ServiceX. This is useful for determining which branches exist in a given dataset before running a full transformation with the correct branch labelling and typing.

It is useful for any lightweight exploration when only metadata or structure information is required without fetching event-level data.

---

##  Overview

The function internally issues a ServiceX request, using python function backend, for the specified dataset(s) and returns a simplified summary of the file structure, such as branches and types in a string formatted for readability.

It accepts both programmatic and command-line usage with parametric return types.

---

## Function

```python
get_structure(datasets, array_out=False, **kwargs)
```

**Parameters:**

- `datasets` (`dict`, `str`, or `list[str]`): One or more datasets to inspect. Made for Rucio DIDs. If a dictionary is used, keys will be used as labels for each dataset in the output string.
- `array_out` (`bool`): If True, empty awkward arrays are reconstructed from the structure information. The function will return a dictionary of ak.Array.type objects. This allows for programmatic access to the dataset structure which can be further manipulated.
- `**kwargs`: Additional arguments forwarded to the helper function `print_structure_from_str`, such as `filter_branch` to apply a filter to displayed branches, `do_print` to print the output during the function call, or `save_to_txt` to save the output to `samples_structure.txt`.

**Returns:**
- `str`: The formatted file structure string.
- `None`: If `do_print` or `save_to_txt` is `True`, the function will print or save the output to a file.
- `dict`: keys are sample names and values are `ak.Array.type` objects with the same dataset structure.

---

## Command-Line Usage

The function is also available as a CLI tool:

```bash
$ servicex-get-structure "scope:dataset-rucio-id" --filter_branch "el_"
```

This dumps to the shell a summary of the structure of the dataset, filtered to branches that contain `"el_"` in their names.

```bash
$ servicex-get-structure "scope:dataset-rucio-id1" "scope:dataset-rucio-id2" --filter_branch "el_"
```

This will output a combined summary of both datasets with the same filter.

---

### Practical Output Example 

Command:

```bash
$ servicex-get-structure  user.mtost:user.mtost.all.Mar11 --filter-branch el_pt 
```

Output on shell: 

```bash
File structure of all samples with branch filter 'el_pt':

---------------------------
📁 Sample: user.mtost:user.mtost.all.Mar11
---------------------------

🌳 Tree: EventLoop_FileExecuted
   ├── Branches:

🌳 Tree: EventLoop_JobStats
   ├── Branches:

🌳 Tree: reco
   ├── Branches:
   │   ├── el_pt_NOSYS ; dtype: AsJagged(AsDtype('>f4'), header_bytes=10)
   │   ├── el_pt_EG_RESOLUTION_ALL__1down ; dtype: AsJagged(AsDtype('>f4'), header_bytes=10)
   │   ├── el_pt_EG_RESOLUTION_ALL__1up ; dtype: AsJagged(AsDtype('>f4'), header_bytes=10)
   │   ├── el_pt_EG_SCALE_ALL__1down ; dtype: AsJagged(AsDtype('>f4'), header_bytes=10)
   │   ├── el_pt_EG_SCALE_ALL__1up ; dtype: AsJagged(AsDtype('>f4'), header_bytes=10)
```

The output lists all trees and branch names matching the specified filter pattern for each requested dataset. 
It shows the branch data type information as interpreted by `uproot`. This includes the vector nesting level (jagged arrays) and the base type (e.g., f4 for 32-bit floats).


#### JSON input 

A json file can be used as input to simplify the command for multiple samples.

```bash
$ servicex-get-structure "path/to/datasets.jsosn" 
```

With `datasets.json` containing:

```
{
  "Signal": "mc23_13TeV:signal-dataset-rucio-id",
  "Background W+jets": "mc23_13TeV:background-dataset-rucio-id1",
  "Background Z+jets": "mc23_13TeV:background-dataset-rucio-id2",
  "Background Drell-Yan": "mc23_13TeV:background-dataset-rucio-id3",
}
```

---

## Programmatic Example

Similarly to the CLI functionality, the output string containing the dataset structure can be retrieved such as:

```python
from servicex_analysis_utils import get_structure

# Retrieve structure of a specific dataset
file_structure=get_structure("mc23_13TeV:some-dataset-rucio-id")
```

### Other options

With `do_print` and `save_to_txt`, the dataset-structure string can instead be routed to std_out or to a text file in the running path.

```python
from servicex_analysis_utils import get_structure

# Directly dump structure to std_out
get_structure("mc23_13TeV:some-dataset-rucio-id", do_print=True)
# Save to samples_summaty.txt
get_structure("mc23_13TeV:some-dataset-rucio-id", save_to_txt=True)
```


#### Return awkward array type


If `array_out` is set to `True` the function reconstructs dummy arrays with the correct structre and return their `Awkward.Array.type` object. 

```python
from servicex_analysis_utils import get_structure

DS = {"sample1": "user.mtost:user.mtost.all.Mar11"}
ak_type = get_structure(DS, array_out=True)

rec = ak_type["sample1"].content #get RecordType

# Find index of reco tree and runNumber branch
reco_idx = rec.fields.index("reco")
branch_idx = rec.contents[reco_idx].fields.index("runNumber")

print("Type for branch 'runNumber':", rec.contents[reco_idx].contents[branch_idx])
```
Output:

```bash
Type for branch 'runNumber': var * int64
```

---

## Notes

- The function does not retrieve event data — only structure/metadata.
- When using `json` input to the CLI, the same branch filtering will be applied to all samples.
- Many types will show as None or unknown when they are not interpretable by the uproot or fail to be reconstructed to ak.arrays
