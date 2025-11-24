from example_solution import my_list as my_list
#!cut_imports!#
def test_my_list():
    # Test is arbitrary, but you should use assert.
    assert type(my_list(7)) is list, "It seems that your function does not return a list but some other type."
    assert len(my_list(7)) == 7, "It seems that the number of created elements is not correct."
    assert len(my_list(0)) == 0, "Your function does not seem to work for the input 0."