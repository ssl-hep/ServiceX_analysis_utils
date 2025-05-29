import awkward as ak
import pytest

from servicex_analysis_utils import read_buffers


def test_simple_record_typetracer():
    arr = ak.Array([{"x": [1, 2, 3], "y": [4, 5]}])

    form = arr.layout.form
    tracer, report = read_buffers.build_typetracer(form)

    # “Touch” one of the two fields
    _ = tracer["x"] + 0

    # Collect the branches and assert exactly one branch is needed (x)
    touched_branches = read_buffers.necessary_branches(report)
    assert set(touched_branches) == {"x"}
