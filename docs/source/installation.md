# Installation

This section provides instructions for installing the ServiceX Analysis Utilities package.

## Prerequisites

Before installing, ensure the following requirements are satisfied:

- Python 3.9 or higher is installed.
- `pip` is updated to the latest version (`pip install --upgrade pip`).
- Access to a ServiceX endpoit is granted
- A valid `servicex.yaml` configuration file is on your local machine.

For instructions on setting up ServiceX, refer to the [ServiceX Installation Guide](https://servicex-frontend.readthedocs.io/en/stable/connect_servicex.html).

## Installation from PyPI

The package is available on PyPI and can be installed via:

```bash
pip install servicex-analysis-utils
```

## Installation from Source

Alternatively, the package can be installed from the GitHub repository:

```bash
git clone https://github.com/ssl-hep/ServiceX_analysis_utils.git
cd ServiceX_analysis_utils
pip install .
```

## Verifying the Installation

After installation, you can verify that the package is accessible by running:

```bash
python -c "import servicex_analysis_utils"
```

No output indicates a successful installation.
