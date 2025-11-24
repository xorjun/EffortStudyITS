# Variational Autoencoder Sampling

Write a python function `vae_sampling` that can sample new data from a variational autoencoder.

Your function should accept the following inputs.

- `mu`: a mean in the latent space (a number or a numpy array)
- `sigma`: a standard deviation in the latent space (a number or a numpy array of matching size to mu)
- `dec`: a decoder that maps a latent space sample to a data point when called as `x = dec(z)`

Your function should return the newly sampled point.

**HINT:** Consider that you need to sample the latent variable `z` yourself, using the re-parametrization trick.
