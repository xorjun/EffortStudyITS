from example_solution import total_study_time as total_study_time
#!cut_imports!#

def test_total_study_time():
    assert total_study_time([]) == 0, "For an empty session list, the total should be 0."
    assert total_study_time([["Mathematics", 45]]) == 45, "Add the duration of a single session correctly."
    assert total_study_time([["Mathematics", 45], ["Physics", 30], ["Biology", 15]]) == 90, "Sum all session durations with an accumulator variable."