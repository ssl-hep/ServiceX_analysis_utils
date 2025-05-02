# ServiceX analysis utils
This repository hosts tools that depend on the [ServiceX Client](https://github.com/ssl-hep/ServiceX_frontend/tree/master). These tools facilitate `ServiceX`'s general usage and offer specific features that replace parts of an analyser workflow.

### To install 
```
pip install servicex-analysis-utils
```
#### Requirements
This package depends requires a `servicex.yml` configuration file granting access to one endpoint with a deployed ServiceX backend.

### This package contains: 
#### `to_awk()`:
```
Load an awkward array from the deliver() output with uproot or uproot.dask.

Parameters:
    deliver_dict (dict): Returned dictionary from servicex.deliver()
                        (keys are sample names, values are file paths or URLs).
    dask (bool):        Optional. Flag to load as dask-awkward array. Default is False
    iterator(bool):      Optional. Flag to materialize the data into arrays or to return iterables with uproot.iterate
    **kwargs :   Optional. Additional keyword arguments passed to uproot.dask, uproot.iterate and from_parquet


Returns:
    dict: keys are sample names and values are awkward arrays, uproot generator objects or dask-awkward arrays.
```


#### `get-structure()`:

```
    Creates and sends the ServiceX request from user inputed datasets to retrieve file stucture.
    Calls print_structure_from_str() to dump the structure in a user-friendly format

    Parameters:
      datasets (dict,str,[str]): The datasets from which to print the file structures.
                                 A name can be given as the key of each dataset in a dictionary  
      kwargs : Arguments to be propagated to print_structure_from_str, e.g filter_branch
```

Function can be called from the command line, e.g: 

```
$ servicex-get-structure "mc23_13TeV:some-dataset-rucio-id" --filter_branch "truth"
```

## Documentation
The different functions are documented in [readthedcos](https://servicex-analysis-utils.readthedocs.io/en/latest/file_introspecting.html) 
