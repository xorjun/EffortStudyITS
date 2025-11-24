#!function!#
import numpy as np

def user_similarity_cosine(x, y):
#!prefix!#
    if len(x) != len(y):
        raise Exception("Different number of elements in the ratings of user1 and user2")

    return (x @ y) / (np.linalg.norm(x) * np.linalg.norm(y))
