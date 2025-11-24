from example_solution import simulate_dice_rolls as simulate_dice_rolls
import numpy as np
#!cut_imports!#


def test_simulate_dice_rolls():

    avg = simulate_dice_rolls(1000)
    assert np.isclose(avg, 3.5, atol = 0.3), "You may have configured your range wrong. Note that the sides of a die are labeled from 1 to 6 (inclusive). Therefore, dice rolls, the average should be around 3.5. But we got %g in our test" % avg

    
    num_rolls1 = 1000
    random_seed1 = 42
    average_value1 = simulate_dice_rolls(num_rolls1, random_seed1)
    
    expected_average1 = 3.5
    assert np.isclose(average_value1, expected_average1, atol=0.1), "It seems, that the average you found is too far from expected 3.5. While it might be an outlier, it is worth it to double-check the code."

    num_rolls2 = 1000
    random_seed2 = 42
    average_value2 = simulate_dice_rolls(num_rolls2, random_seed2)
    assert np.isclose(average_value1, average_value2, atol=0.1), "It seems, that the average you found is too far from expected 3.5. While it might be an outlier, it is worth it to double-check the code. "

    num_rolls0 = 1
    random_seed0 = 4
    average_value0 = simulate_dice_rolls(num_rolls0, random_seed0)
    expected_average0 = 3.0
    assert average_value0 == expected_average0, "It may be that you did not include the random seed properly."

    num_rolls3 = 1
    random_seed3 = 27
    average_value3 = simulate_dice_rolls(num_rolls3, random_seed3)
    assert not np.isclose(average_value1, average_value3, atol=0.1), "It seems that the np.random.seed() was not included as an argument."
