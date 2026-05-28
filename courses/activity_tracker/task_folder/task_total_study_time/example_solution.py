#!function!#
def total_study_time(sessions: list):
#!prefix!#
    total_minutes = 0
    for session in sessions:
        total_minutes += session[1]
    return total_minutes