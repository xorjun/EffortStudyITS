#!function!#
import numpy as np
def hmm_sampling(pi, A, B):
#!prefix!#
    n, _ = A.shape

    if len(pi) != n:
      raise ValueError('pi should have as many entries as A has rows.')

    if A.shape[1] != n+1:
      raise ValueError('A should have one more column than rows for the ending probabilities')

    _, K = B.shape

    if B.shape[0] != n:
      raise ValueError('B should have as many rows as A')

    h = []
    x = []
    # choose the starting state
    h_next = np.random.choice(n, p = pi, size = 1)[0]

    # continue until ending
    while h_next != n:
      h.append(h_next)
      # choose the next symbol
      i = h[-1]
      x.append(np.random.choice(K, p = B[i, :], size = 1)[0])
      # choose the next state
      h_next = np.random.choice(n+1, p = A[i, :], size = 1)[0]

    return h, x
