from example_solution import wilcoxon_usage as wilcoxon_usage
#!cut_imports!#
import numpy as np

def test_wilcoxon_usage():
    p_control, p_intervention = wilcoxon_usage()

    assert type(p_control) in [int, np.int32, np.int64, float, np.float64], f"Return type should be numeric, not {type(res)}"
    assert type(p_intervention) in [int, np.int32, np.int64, float, np.float64], f"Return type should be numeric, not {type(res)}"

    assert np.abs(p_control - 3.55492e-06) < 1E-6, f"Unexpected p-value for the control group. Maybe you used the wilcoxon function incorrectly?"
    assert np.abs(p_intervention - 2.52876e-06) < 1E-6, f"Unexpected p-value for the intervention group. Maybe you used the wilcoxon function incorrectly?"