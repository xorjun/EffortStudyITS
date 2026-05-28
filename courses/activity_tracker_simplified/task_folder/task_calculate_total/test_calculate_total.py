from example_solution import total_activity_time as total_activity_time
#!cut_imports!#

def test_calculate_total():
    assert total_activity_time([]) == 0, "For an empty list, the total should be 0."
    assert total_activity_time([20, 30, 10]) == 60, "Sum all times in the list correctly."
    assert total_activity_time([10]) == 10, "A single item should return that item's value."
    assert total_activity_time([5, 5, 5, 5]) == 20, "Sum all items in the list."
