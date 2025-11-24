#!function!#
import numpy as np

def vae_sampling(mu, sigma, dec):
#!prefix!#
    """ Implements variational autoencoder sampling. """
    if type(mu) in [int, float]:
        eps = np.random.randn(1)
    else:
        eps = np.random.randn(*mu.shape)
    z = mu + sigma * eps
    return dec(z)