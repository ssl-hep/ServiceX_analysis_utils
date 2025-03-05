# ServiceX analysis utils
This repository provides analysis tools to be used with the [ServiceX Client](https://github.com/ssl-hep/ServiceX_frontend/tree/master)

### To install 
```
pip install servicex-analysis-utils
```

##### This package contains the to_awk() function:
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

## Documentation
The different functions are documented in TBD 
