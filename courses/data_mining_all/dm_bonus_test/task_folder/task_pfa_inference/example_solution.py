#!function!#
import numpy as np
def pfa_inference(X, Q, beta, gamma, rho):
#!prefix!#

    n, K = Q.shape

    # initialize the output matrix
    Theta = np.zeros((X.shape[0]+1, K))
    Theta[0, :] = beta

    # start inferring
    for t in range(X.shape[0]):
      j = X[t, 0]
      for k in range(K):
        if Q[j, k] > 0.5:
          if X[t, 1] > 0.5:
            Theta[t+1, k] = Theta[t, k] + gamma[k]
          else:
            Theta[t+1, k] = Theta[t, k] + rho[k]

    return Theta[1:, :]
