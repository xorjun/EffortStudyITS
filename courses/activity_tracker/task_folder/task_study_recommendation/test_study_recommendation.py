from example_solution import study_recommendation as study_recommendation
#!cut_imports!#

def test_study_recommendation():
    assert study_recommendation(0) == "Study a little longer today.", "Return the short-study message for totals below 60 minutes."
    assert study_recommendation(59) == "Study a little longer today.", "Totals below 60 minutes should use the first message."
    assert study_recommendation(60) == "Great job! You reached at least 60 minutes.", "At 60 minutes and above, return the success message."
    assert study_recommendation(120) == "Great job! You reached at least 60 minutes.", "The success message should also be returned for larger totals."