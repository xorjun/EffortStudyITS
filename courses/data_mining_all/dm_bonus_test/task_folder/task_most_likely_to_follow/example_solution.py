#!function!#
import random
from collections import defaultdict

def most_likely_to_follow(strings, x):

#!prefix!#
    # Dictionary to hold counts of following characters
    transitions = defaultdict(lambda: defaultdict(int))
    
    # Iterate through each string
    for string in strings:
        for i in range(len(string)):
            if string[i] == x:
                if i + 1 < len(string):
                    following_char = string[i + 1]
                else:
                    following_char = "end"  # Use "end" for the end of the string
                transitions[x][following_char] += 1
    
    # Create probabilities
    probabilities = {}
    for following_char, count in transitions[x].items():
        total_count = sum(transitions[x].values())
        probabilities[following_char] = count / total_count
    
    if not probabilities:
        return None  # No predictions can be made
    return max(probabilities, key=probabilities.get)  # Get the character with the highest probability
