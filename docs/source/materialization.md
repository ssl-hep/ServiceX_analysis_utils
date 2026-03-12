# Materialization of delivered data

This page covers the usage of `to_awk()` for materializing the output of a ServiceX `deliver()` call into Awkward Arrays, Dask arrays, or iterators, and demonstrates integration with common analysis patterns.

---

## Overview

The `to_awk()` function loads data from the deliver output dictionary, supporting both ROOT (`.root`) and Parquet (`.parquet` or `.pq`) file formats.

It provides flexible options for:

- Direct loading into Awkward Arrays.
- Lazy loading using Dask for scalable operations.
- Returning iterator objects for manual control over file streaming.

## Function 

```python
to_awk(deliver_dict, dask=False, iterator=False, **kwargs)
```

**Parameters:**

- `deliver_dict` (dict): Dictionary returned by `servicex.deliver()`. Keys are sample names, values are file paths or URLs.
- `dask` (bool, optional): If True, loads files lazily using Dask. Default is False.
- `iterator` (bool, optional): If True and not using Dask, returns iterators instead of materialized arrays. Default is False.
- `**kwargs`: Additional keyword arguments passed to `uproot.dask`, `uproot.iterate`, dak.from_parquet, or `awkward.from_parquet`.

**Returns:**

- `dict`: A dictionary where keys are sample names and values are either Awkward Arrays, Dask Arrays, or iterators. It keeps the same structure as the `deliver` output dict. 

---

## Usage Examples

### Simple Materialization

Load ServiceX deliver results directly into Awkward Arrays:

```python
from servicex_analysis_utils import to_awk
from servicex import query, dataset, deliver

spec = {
    "Sample": [
        {
            "Name": "simple_transform",
            "Dataset": dataset.FileList(
                ["root://eospublic.cern.ch//eos/opendata/atlas/rucio/data16_13TeV/DAOD_PHYSLITE.37019878._000001.pool.root.1"]  # noqa: E501
            ),
            "Query": query.FuncADL_Uproot()
            .FromTree("CollectionTree")
            .Select(lambda e: {"el_pt": e["AnalysisElectronsAuxDyn.pt"]}), 
        }
    ]
}

arrays=to_awk(deliver(spec))
```

### Lazy Loading with Dask

Results are loaded lazily for large datasets using Dask task graphs, enabling parallel execution across multiple workers.

```python
import dask_awkward as dak

dask_arrays = to_awk(deliver(spec), dask=True)
el_pt_array = dask_arrays["simple_transform"]["el_pt"]
mean_el_pt = dak.mean(el_pt_array).compute()
```

### Using Iterators

Iterators are returned instead of materialized arrays to avoid loading excessive data into memory. This option requires `dask=False` (the default). The following example loads 10,000 events per chunk:

```python
iterables = to_awk(deliver(spec), iterator=True, step_size=10000)
```

The data chunks can then be processed individually:

```python
for chunk in iterables['simple_transform']:
    # process small chunk (~10k events)
    analyse(chunk) #some function for el_pt
```

All events can also be concatenated into a single array:

```python
import awkward as ak
arrays= ak.concatenate(list[iterables['simple_transform']])
```

---


## Multiple Samples

ServiceX queries allow multiple sample transformations. The `to_awk()` function allows straightforward handling of such requests, enabling seamless integration with analysis frameworks where multiple samples are manipulated separately after being passed through the same transformation using `deliver()`.

```python
from servicex_analysis_utils import to_awk
import awkward as ak

# Given a ServiceX deliver return
deliver_result = {
    "Signal": ["path/to/signal_file1.root", "path/to/signal_file2.root"],
    "Background": ["path/to/background_file.root"]
}

arrays = to_awk(deliver_result)

signal_el_pt = arrays["Signal"]["el_pt"]
background_el_pt = arrays["Background"]["el_pt"]

mean_signal = ak.mean(signal_el_pt)
mean_background = ak.mean(background_el_pt)

print(f"Mean electron pT (Signal): {mean_signal:.2f} GeV")
print(f"Mean electron pT (Background): {mean_background:.2f} GeV")
```


## Notes

- **Multiple samples:** For transformations delivering multiple samples, `dask` and `iterator` options are applied homogeneously to all samples.
- **Error Handling:** In case of loading errors, the affected sample has `None` as its value in the returned dictionary.
- **Supported Formats:** A custom dictionary (non-ServiceX) can be provided, but the paths must be either ROOT or Parquet format.
- **Branch Filtering, others:** Additional `**kwargs` allow specifying branch selections or other loading options supported by `uproot`, `awkward` and `dask_awkward`.

