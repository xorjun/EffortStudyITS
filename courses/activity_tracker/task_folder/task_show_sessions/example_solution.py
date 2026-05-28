#!function!#
def show_sessions(sessions: list):
#!prefix!#
    for session in sessions:
        print(f"Subject: {session[0]}, Duration: {session[1]} minutes")