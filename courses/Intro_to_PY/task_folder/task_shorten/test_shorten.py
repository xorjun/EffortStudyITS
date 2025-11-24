from example_solution import shorten as shorten
#!cut_imports!#
def test_shorten():
    # Test is arbitrary, but you should use assert.
    try:
        assert shorten([]) == [], "For the empty list, the function should return an empty list."
    except IndexError:
        assert False, "For the empty list, the function should return an empty list."
    assert shorten([1]) == [1, 1], "For a one-element list the function should return a new list with two copies of this element."
    assert shorten([0,1,2,3,4,5,6,7]) == [0, 7], "It seems that some elements are not there or have a wrong format. For example, tuples are not lists."
    assert shorten(['eggs', 'fruit', 'orange juice', "ham"]) == ['eggs', "ham"], "Are you sure there are the first and the last elements only?"