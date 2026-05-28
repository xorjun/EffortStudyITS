#!function!#
def add_session(sessions: list, subject: str, duration_text: str):
#!prefix!#
    duration = int(duration_text)
    sessions.append([subject, duration])
    return sessions