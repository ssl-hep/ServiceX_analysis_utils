# ServiceX Analysis Utilities

This package provides tools interacting with [ServiceX](https://github.com/ssl-hep/ServiceX_frontend), a data extraction, transformation and delivery system built for ATLAS and CMS analyses on large datasets. The Analysis Utils package offers helper functions that streamline the usage of ServiceX and simplify its integration on workflows. But it also contains specific use case tools that benefit from the service. 

---

## Installation

Install the package from PyPI:

```bash
pip install servicex-analysis-utils
```
More information can be found in [Instalation and requirements](installation.md)

## Documentation Contents

```{toctree}
:maxdepth: 2

installation
materialization
file_introspecting
```

---

## Utility Functions

### `to_awk()`
Load an Awkward Array from ServiceX output easily.

 See detailed usage here: [Materiazlization documentation](materialization.md)

### `get_structure()`
Create and send ServiceX requests to retrieve file structures with a CLI implementation.

 See detailed usage here: [File introspection documentation](file_introspecting.md)