# ServiceX Analysis Utilities

This package provides tools for interacting with [ServiceX](https://github.com/ssl-hep/ServiceX_frontend), a data extraction, transformation, and delivery system built for ATLAS and CMS analyses on large datasets. The Analysis Utils package offers helper functions that streamline ServiceX usage and simplify its integration into analysis workflows. The package also contains specific use-case tools that leverage the service.

---

## Installation

Install the package from PyPI:

```bash
pip install servicex-analysis-utils
```
More information can be found in [Installation and requirements](installation.md)

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
Loads Awkward Arrays from ServiceX `deliver()` output.

Detailed usage is available in [Materialization documentation](materialization.md).

### `get_structure()`
Creates and sends ServiceX requests to retrieve file structures, with a CLI implementation.

Detailed usage is available in [File introspection documentation](file_introspecting.md).