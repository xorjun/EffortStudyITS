#!function!#
import numpy as np
def user_similarity_explicit(x, y):
#!prefix!#
    if len(x) != len(y):
        raise Exception("Different number of elements in the ratings of x and y")

    shared = np.logical_and(np.isfinite(x), np.isfinite(y))

    if np.sum(shared) < 0.5:
      return 0 # No common items, return zero correlation
        
    else:# Compute means
        mean_x = np.nanmean(x)
        mean_y = np.nanmean(y)

        delta_x = x[shared] - mean_x
        delta_y = y[shared] - mean_y

        denominator = np.sqrt(np.sum(delta_x**2)) * np.sqrt(np.sum(delta_y**2))

        if denominator < 1E-8:
          return 0.

        return (delta_x @ delta_y) / denominator
