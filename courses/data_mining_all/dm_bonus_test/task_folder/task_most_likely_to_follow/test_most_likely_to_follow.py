from example_solution import most_likely_to_follow
#!cut_imports!#

import numpy as np

def test_most_likely_to_follow():

        expressions = ['aaaabb', 'aabbaaaaa', 'abaaa']
        target_digit = 'a'
        output = most_likely_to_follow(expressions, target_digit)

        assert (output=='a'), "In the expressions ['aaaabb', 'aabbaaaaa', 'abaaa'], the most likely follower for an a is an a."

        expressions = ['aaaaaab', 'aaaab', 'aab']
        target_digit = 'b'
        output = most_likely_to_follow(expressions, target_digit)
        
        assert (output == "end"), "In the expressions ['aaaaaab', 'aaaab', 'aab'], the most likely follower for a b is an end."
