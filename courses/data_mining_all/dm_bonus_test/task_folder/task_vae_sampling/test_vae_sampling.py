from example_solution import vae_sampling
#!cut_imports!#
import numpy as np

def test_vae_sampling():
    
    mu = 1.
    sigma = 0.
    dec = lambda z : z

    # test basic functionality
    x = vae_sampling(mu, sigma, dec)
    
    assert type(x) in [int, float, np.ndarray], f"The output of vae_sampling should be a number or a vector, not {str(type(x))}"

    if type(x) is np.ndarray:
        assert len(x) == 1, f"The output of vae_sampling should be a single number if called for a 1D latent space, not a vector of length{len(x)}"
        x = x[0]

    assert np.abs(x - mu) < 1E-3, f"If called with mu = 1, sigma = 0, the sampled latent vector z should be exactly 1, not {x}"

    # test distribution properties
    mu = np.array([0., 1.])
    sigma = np.array([0.3, 0.5])
    
    N = 1000
    n = len(mu)
    X = np.zeros((N, n))
    for i in range(N):
        x = vae_sampling(mu, sigma, dec)

        assert type(x) is np.ndarray, f"The output of vae_sampling should be a number a numpy error when called with numpy errors, not {type(x)}"

        assert x.shape == (2,), f"When called with a 2D array, the latent sample z should be a 2D array, as well, not {x.shape}"

        X[i, :] = x

    assert np.sum(np.abs(np.mean(X, axis = 0) - mu)) < 0.1, f"If called with mu = [0, 1], the approximate mean in the latent space should be mu, not {np.mean(X, axis = 0)}"

    assert np.sum(np.abs(np.std(X, axis = 0) - sigma)) < 0.1, f"If called with sigma = [0.3, 0.5], the approximate standard deviation in the latent space should be sigma, not {np.std(X, axis = 0)}"
