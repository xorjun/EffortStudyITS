#!function!#
def study_recommendation(total_minutes: int):
#!prefix!#
    if total_minutes < 60:
        return "Study a little longer today."
    return "Great job! You reached at least 60 minutes."