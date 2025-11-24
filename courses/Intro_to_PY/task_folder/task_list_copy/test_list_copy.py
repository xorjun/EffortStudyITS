from example_solution import list_copy as list_copy
#!cut_imports!#
def test_list_copy():
    # Test is arbitrary, but you should use assert.
    assert list_copy([])[0] == [], "For an empty list the function should return two empty lists"
    assert list_copy([])[1] == [], "For an empty list the function should return two empty lists"
    assert list_copy([1])[0] == [], "For a list with one element, the first output should be empty"
    assert list_copy([1])[1] == [1], "The second output should remain the original list"
    assert list_copy([1, 2])[0] == [], "For a list with two elements, the first output should be empty"
    assert list_copy([1, 2, 3, 4, 5])[0] == [2, 3, 4], "There is an error in creating the new list"
    assert list_copy([1, 2, 3, 4, 5])[1] == [1, 2, 3, 4, 5], "The original list is not preserved"