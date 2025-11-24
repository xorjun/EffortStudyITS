#!function!#
import numpy as np
def ndcg_at_k(user_evaluations, k):
#!prefix!#
    """
    Calculate NDCG at k based on user evaluations.

    Parameters:
    - user_evaluations: List or array of user relevance scores (higher values are more relevant)
    - k: Top k items to consider

    Returns:
    - NDCG at k
    """
    # Ensure the length of user_evaluations is at least k
    if len(user_evaluations) < k:
        raise ValueError("Length of user_evaluations should be at least k.")

    # Sort the user evaluations in descending order
    #sorted_user_evaluations = np.argsort(user_evaluations)[::-1]

    # Calculate DCG (Discounted Cumulative Gain) at k
    dcg_at_k = 0
    for i in range(k):
        dcg_at_k += user_evaluations[i] / np.log2(i+ 2)

    # Sort user evaluations in non-decreasing order
    ideal_sorted_user_evaluations = np.sort(user_evaluations)[::-1]

    # Calculate ideal DCG at k
    ideal_dcg_at_k = 0 
    for i in range(k):
        ideal_dcg_at_k += ideal_sorted_user_evaluations[i] / np.log2(i+ 2)
    

    # Calculate NDCG at k
    ndcg_at_k = dcg_at_k / ideal_dcg_at_k if ideal_dcg_at_k > 0 else 0.0

    return ndcg_at_k

# Example usage:
#user_evaluations = [3, 2, 1, 4, 0, 5]
#k = 3

#result = ndcg_at_k_user_eval(user_evaluations, k)
#print(result)
#print(f"NDCG at {k}: {result}")

