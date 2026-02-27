import pytest
import numpy as np
import uproot
import awkward as ak
from servicex_analysis_utils import to_awk


@pytest.fixture
def build_multi_rntuple(tmp_path):
    """
    Create ROOT file with two RNTuples:
    - 'servicex'
    - 'someotherobject'
    """
    file_path = tmp_path / "multi_rntuple.root"

    branch1 = np.arange(10, dtype=np.int32)
    branch2 = np.ones(10, dtype=np.float64) * 42.0

    with uproot.recreate(file_path) as f:
        f.mkrntuple(
            "servicex",
            {"branch1": branch1, "branch2": branch2},
        )
        f.mkrntuple(
            "someotherobject",
            {"branch1": branch1, "branch2": branch2},
        )

    return str(file_path)


def test_multiple_keys_warning_and_content(build_multi_rntuple, caplog):
    caplog.set_level("WARNING")

    result = to_awk({"test": [build_multi_rntuple]})

    # ---- Check warning emitted ----
    assert any(
        "Multiple keys found in ROOT file" in record.message
        for record in caplog.records
    )

    arr = result["test"]

    # ---- Check return type ----
    assert isinstance(arr, ak.Array)

    # ---- Check content correctness ----
    # branch1 = np.arange(10) -> mean = 4.5
    assert float(ak.mean(arr["branch1"])) == 4.5

    # branch2 = all 42 -> mean = 42
    assert float(ak.mean(arr["branch2"])) == 42.0
