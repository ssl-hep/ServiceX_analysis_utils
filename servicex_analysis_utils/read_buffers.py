# Copyright (c) 2025, IRIS-HEP
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import awkward as ak
from awkward.forms import RecordForm


def add_keys(original_form):
    """
    Add a form_key to the parent Record and to every child ListOffset/content associated to a field.

        Parameters:
        original_form (ak.forms.Form): Form of the awkward array the typetracer will be built upon.
                                       This should be a RecordForm, which contains fields and contents.

    Returns:
        RecordForm:
    """

    # RecordForm: zip contents + field names, recurse on each child,
    # then rebuild with each child's form_key set to its field name
    if isinstance(original_form, RecordForm):
        new_contents = []
        for child, name in zip(original_form.contents, original_form.fields):
            child = child.copy(form_key=name)
            new_contents.append(child)
        return RecordForm(
            new_contents,
            original_form.fields,
            form_key="RecordForm_key",  # Give name to parent RecordForm
            parameters=original_form.parameters,
        )

    else:
        raise ValueError(
            f"Unsupported form type: {type(original_form)}. "
            "This function only supports RecordForm."
        )


def is_branch_buffer(form_key, attribute, form):
    # rename any node that has no form_key
    if form_key is None:
        return "Not-a-branch"
    return f"{form_key}"


def build_typetracer_with_report(form):
    """
    Build a typetracer from an awkward form, adding keys to the RecordForm and ListOffsetForm.

        Parameters:
        form (ak.forms.Form): Form of the awkward array the typetracer will be built upon.

    Returns:
        tracer, report: ak.typetracer.TypeTracer: the typetracer built from the array form.
    """
    stamped_form = add_keys(form)

    tracer, report = ak.typetracer.typetracer_with_report(
        stamped_form,
        buffer_key=is_branch_buffer,
        highlevel=True,
        behavior=None,
        attrs=None,
    )
    return tracer, report


def get_necessary_branches(report):
    """
    Utility function to get the necessary branches from a typetracer report.

        Parameters:
        report (ak.typetracer.Report): Report from the typetracer.

    Returns:
        list: List of necessary branches.
    """
    return [
        br for br in report.data_touched if br != "Not-a-branch"
    ]  # filter out "Not-a-branch"
