from example_solution import add_session as add_session
#!cut_imports!#

def test_add_session():
    result = add_session([], "Mathematics", "45")
    assert type(result) is list, "The function should return a list of sessions."
    assert result == [["Mathematics", 45]], "Append the subject together with the converted integer duration."
    assert add_session([], "Physics", "30")[0][1] == 30, "Convert the duration text to an integer before storing it."
    assert add_session([["Mathematics", 45]], "Physics", "30") == [["Mathematics", 45], ["Physics", 30]], "Append new sessions to the existing list instead of starting over."