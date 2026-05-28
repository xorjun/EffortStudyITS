from example_solution import irt_two
#!cut_imports!#
import numpy as np

def test_irt_two():

    # Test a trivial case
    abilities = np.array([-1, +1])
    x = np.array([0, 1])
    a, b = irt_two(abilities, x)
    assert abs(b) < 0.1, f"For two students with abilities -1 and +1 where the first fails and the second succeeds, the difficulty should be exactly at zero but was {b}"

    # Test another trivial case
    abilities = np.array([0, 2])
    x = np.array([0, 1])
    a, b = irt_two(abilities, x)
    assert abs(b - 1) < 0.1, f"For two students with abilities 0 and 2 where the first fails and the second succeeds, the difficulty should be around 1 but was {b}"
    
    
    # Test unsolvable trivial case
    abilities = np.array([0, 0])
    x = np.array([0, 1])
    a, b = irt_two(abilities, x)
    assert abs(a) < 0.1, f"For two students with the same ability, one of which fails and one of which succeeds, no meaningful model should result and a should be close to zero, but we got a = {a}"
    
    # Test for a more complicated case
    N = 100
    abilities = np.random.randn(N)
    a_true = 2.
    b_true = 1.
    p = 1. / (1. + np.exp(-a_true*(abilities - b_true)))
    x = np.random.rand(N) < p

    a, b = irt_two(abilities, x)

    assert abs(b_true - b) < .4, f"Tested an example case with true b = {b_true} but got b = {b}"
    assert abs(a_true - a) < 1., f"Tested an example case with true a = {a_true} but got a = {a}"