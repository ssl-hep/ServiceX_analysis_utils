import awkward as ak
from awkward.forms import ListOffsetForm, NumpyForm
import pytest
from servicex_analysis_utils import read_buffers
from skhep_testdata import data_path
import uproot


@pytest.fixture
def setup_form():
    # Create a simple awkward array with a RecordForm
    arr = ak.Array([{"x": [1, 2, 3], "y": [4, 5]}])
    form = arr.layout.form

    # Build a form from a .root file
    file = data_path("uproot-Zmumu.root") + ":events"
    array = uproot.open(file).arrays(library="ak")
    return form, array.layout.form


@pytest.fixture
def setup_type_tracer(setup_form, from_uproot):
    array_form, uproot_form = setup_form
    if from_uproot:
        form = uproot_form
    else:
        form = array_form
    # Build a typetracer with the form
    tracer, report = read_buffers.build_typetracer_with_report(form)
    return tracer, report


def test_instance_of_record_form(setup_form):
    simple_form, root_form = setup_form
    # Check instances of RecordForm
    assert isinstance(
        simple_form, ak.forms.RecordForm
    ), f"Form is {type(simple_form)}, but should be RecordForm"

    assert isinstance(
        root_form, ak.forms.RecordForm
    ), f"Form is {type(root_form)}, but should be RecordForm"


@pytest.mark.parametrize("from_uproot", [True, False])
def test_built_typetracer_instance(setup_type_tracer):
    tracer, report = setup_type_tracer
    # Check if the tracer is an instance of high-level Array
    assert isinstance(
        tracer, ak.highlevel.Array
    ), f"Tracer should be a highlevel Array but is {type(tracer)}"

    # Check if the report is an instance of Report
    assert isinstance(report, ak.typetracer.TypeTracerReport), "Report is not a Report"
    # Check if the report has data_touched
    assert hasattr(
        report, "data_touched"
    ), "Report does not have data_touched attribute"


@pytest.mark.parametrize("from_uproot", [False])
def test_simple_record_typetracer(setup_type_tracer):
    tracer, report = setup_type_tracer

    assert tracer.fields == ["x", "y"], "Fields of the tracer do not match expected"

    # “Touch” one of the two fields
    _ = tracer["x"] + 0

    # Collect the touched branches
    touched_branches = read_buffers.get_necessary_branches(report)
    assert set(touched_branches) == {"x"}


@pytest.mark.parametrize("from_uproot", [True])
def test_root_record_typetracer(setup_type_tracer):
    tracer, report = setup_type_tracer
    expected_fields = [
        "Type",
        "Run",
        "Event",
        "E1",
        "px1",
        "py1",
        "pz1",
        "pt1",
        "eta1",
        "phi1",
        "Q1",
        "E2",
        "px2",
        "py2",
        "pz2",
        "pt2",
        "eta2",
        "phi2",
        "Q2",
        "M",
    ]

    assert (
        tracer.fields == expected_fields
    ), "Fields of the tracer do not match expected"

    # Compute deltaR on typetracer
    delta_r = (
        (tracer["eta1"] - tracer["eta2"]) ** 2 + (tracer["phi1"] - tracer["phi2"]) ** 2
    ) ** 0.5

    # Check delta_r is still an array
    assert isinstance(
        delta_r, ak.highlevel.Array
    ), f"delta_r should be a highlevel Array but is {type(delta_r)}"

    # Check no data is loaded in computation
    # only TypeTracer placeholders should be present
    first_element = delta_r[0]
    assert "TypeTracer" in repr(
        first_element
    ), f"Expected a TypeTracer placeholder, got {repr(first_element)} instead."

    # Collect the touched branches
    touched_branches = read_buffers.get_necessary_branches(report)
    assert set(touched_branches) == {
        "eta1",
        "phi1",
        "eta2",
        "phi2",
    }, "Touched branches do not match expected branches"


def test_error_on_wrong_form():
    # Test that ValueError is raised when an empty form is passed
    with pytest.raises(
        ValueError,
        match="Unsupported form type: <class 'NoneType'>. This function only supports RecordForm.",
    ):
        read_buffers.add_keys(None)

    # Test that ValueError is raised when another form type is passed
    dummy = ListOffsetForm("i64", NumpyForm("int32"))
    with pytest.raises(
        ValueError,
        match="Unsupported form type: <class 'awkward.forms.listoffsetform.ListOffsetForm'>. This function only supports RecordForm.",
    ):
        read_buffers.add_keys(dummy)
