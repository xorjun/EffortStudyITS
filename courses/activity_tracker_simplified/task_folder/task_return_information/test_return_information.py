from example_solution import get_subject as get_subject
#!cut_imports!#

def test_return_information():
    assert get_subject() == "Mathematics", "The function should return 'Mathematics'."
    assert type(get_subject()) is str, "The return value should be a string."
