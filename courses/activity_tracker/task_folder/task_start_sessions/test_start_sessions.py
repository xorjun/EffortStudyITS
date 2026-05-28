from example_solution import start_sessions as start_sessions
#!cut_imports!#

def test_start_sessions():
    result = start_sessions()
    assert type(result) is list, "The function should return a list."
    assert result == [], "Create an empty list named sessions and return it."
    assert start_sessions() == [], "The function should always return a new empty list."