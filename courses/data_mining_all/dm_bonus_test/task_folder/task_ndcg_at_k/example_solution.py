#!function!#
import numpy as np
def ndcg_at_k(relevance, k):
#!prefix!#
    """
    Calculate NDCG at k based on user evaluations.

    Parameters:
    - relevance: array of user relevance scores (higher values are more relevant)
    - k: int; the maximum rank considered

    Returns:
    - NDCG
    """
    if len(relevance) > k:
      ideal_relevance = -np.sort(-relevance)[:k]
      relevance = relevance[:k]
    else:
      ideal_relevance = -np.sort(-relevance)


    # function for dcg calculation
    def dcg(r):
      return np.sum(r / np.log2(2 + np.arange(len(r))))

    return dcg(relevance) / dcg(ideal_relevance)

