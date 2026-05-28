from example_solution import start_sessions as start_sessions
#!cut_imports!#

def test_store_sessions():
    result = start_sessions()
    assert type(result) is list, "The function should return a list."
    assert result == ["Python", "Mathematics"], "The list should contain 'Python' and 'Mathematics' in that order."
    assert len(result) == 2, "The list should contain exactly two items."
    assert start_sessions() == ["Python", "Mathematics"], "The function should always return the same list."
