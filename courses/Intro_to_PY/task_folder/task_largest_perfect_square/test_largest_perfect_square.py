from example_solution import largest_perfect_square as largest_perfect_square
import math
#!cut_imports!#
def test_largest_perfect_square():
    # Test is arbitrary, but you should use assert.
    numbers1 = [1, 4, 9, 16, 25]
    numbers2 = [8, 10, 15, 18, 20]
    numbers3 = [49, 64, 81, 121, 100]
    assert largest_perfect_square(numbers1) == 25, "It seems that the largest perfect square is not found correctly."
    assert largest_perfect_square([]) == None, "For an empty list, we expect None as output."
    assert largest_perfect_square(numbers2) == None, "For an array with no perfect squares (such as [8, 11]), we expect None as output."
    assert largest_perfect_square(numbers3) == 121, "In a list containing multiple perfect squares, we expect the largest one (not the first or last)."