#Implement further tests in a seperate file each
from example_solution import smallest_above
#!cut_imports!#
def test_smallest_above():
    # Test is arbitrary, but you should use assert.
    numbers1 = [1, 2, 3, 4, 5]
    numbers2 = [-2, -1, 0, 5, 7, 2, -4]
    numbers3 = [-1, -2, -3, -4, -5]
    threshold = 2
    assert smallest_above(numbers1, threshold) == 3, "It seems that the smallest number above the threshold is found wrong. For example, for the list [1, 2, 3, 4, 5] and the threshold 2, we would expect the answer to be 3."
    assert smallest_above(numbers2, threshold) == 5, "It seems that the smallest number above the threshold is found wrong. Perhaps you are not considering elements that are strictly larger?"
    assert smallest_above(numbers3, threshold) is None, "It seems that you forgot a condition, when there is no number aobe threshold in the list."
    
