from example_solution import describe_session as describe_session
#!cut_imports!#

def test_describe_session():
    assert describe_session(["Mathematics", 45]) == "session[0] = Mathematics, session[1] = 45", "Use list indices 0 and 1 in the returned string."
    assert describe_session(["Computer Science", 90]) == "session[0] = Computer Science, session[1] = 90", "The function should work for different session values."