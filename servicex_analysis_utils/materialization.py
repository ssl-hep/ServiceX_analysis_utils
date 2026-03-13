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

import uproot
import awkward as ak
import logging


def to_awk(deliver_dict, return_iterator=False, **kwargs):
    """
    Load an awkward array from the deliver() output using uproot.

    Parameters:
        deliver_dict (dict): Returned dictionary from servicex.deliver()
                             (keys are sample names, values are file paths or URLs).
        return_iterator(bool): Optional. If True, return uproot.iterate generator.
                               Otherwise materialize the data into awkward arrays.
        **kwargs : Optional. Additional keyword arguments passed to uproot.iterate
                   and ak.from_parquet

    Returns:
        dict: keys are sample names and values are awkward arrays or uproot iterators.
    """

    if not deliver_dict:
        raise RuntimeError("Input dict from servicex.deliver cannot be empty.")

    awk_arrays = {}

    for sample, paths in deliver_dict.items():

        if not paths:
            raise RuntimeError(
                f"Delivered result file path list for {sample} is empty."
            )

        # Determine file type
        f_type = str(paths[0])

        if ".root" in f_type:
            is_root = True
        elif ".parquet" in f_type or ".pq" in f_type:
            is_root = False
        else:
            raise RuntimeError(
                f"Unsupported delivered format: '{paths[0]}'. Must be .root or Parquet (.parquet, .pq)"
            )

        try:

            if is_root:

                # Inspect ROOT file to find TTree or RNTuple
                with uproot.open(paths[0]) as f:

                    keys = f.keys()

                    if len(keys) == 0:
                        raise RuntimeError(
                            f"No keys found in ROOT file for sample {sample}. Check file content."
                        )

                    valid_object = None
                    valid_keys = []

                    for key in keys:

                        obj = f[key]
                        classname = obj.classname

                        # Check if classname contains TTree or RNTuple
                        if "TTree" in classname or "RNTuple" in classname:
                            valid_keys.append(key)

                            if valid_object is None:
                                valid_object = key.split(";")[0]

                    if valid_object is None:
                        raise RuntimeError(
                            f"No TTree or RNTuple found in ROOT file for sample {sample}."
                        )

                    if len(valid_keys) > 1:
                        logging.warning(
                            f"Multiple TTrees/RNTuples found in ROOT file for sample {sample}. "
                            f"Using the first one: {valid_object} from keys: {valid_keys}"
                        )

                # Prepare paths for iterate
                paths_iterate = [f"{path}:{valid_object}" for path in paths]

                iterators = uproot.iterate(
                    paths_iterate,
                    library="ak",
                    **kwargs,
                )

                if return_iterator:

                    awk_arrays[sample] = iterators

                else:

                    it_arrays = list(iterators)

                    if it_arrays == []:

                        logging.warning(
                            f"Sample {sample} has no data to load. Returning empty array."
                        )

                        awk_arrays[sample] = ak.Array([])

                    else:

                        awk_arrays[sample] = ak.concatenate(it_arrays)

            else:

                # Parquet loading
                awk_arrays[sample] = ak.from_parquet(paths, **kwargs)

        except Exception:

            msg = f"\nError loading sample: {sample}"
            logging.error(msg, exc_info=True, stacklevel=2)

            awk_arrays[sample] = None

    return awk_arrays
