from example_solution import second_sum as second_sum
#!cut_imports!#
def test_second_sum():
    assert second_sum([]) == 0, "For the empty list, the result should be zero."
    assert second_sum([3]) == 0, "For a list with only one element, the result should be zero."
    assert second_sum([3, 6]) == 6, "For a list with two elements, the result should be the second element."
    assert second_sum([1, 2, 3, 4, 5]) == 6, "It seems that the sum was calculated incorrectly. For the list [1, 2, 3, 4, 5], we would expect 2 + 4 = 6 as a result."
    assert second_sum([9, 10, 16, 8, 0,7,5,3,2]) == 28, "It seems that the sum was calculated incorrectly."
    
