# Deep Learning: Variational Autoencoders

Consider the following code to generate samples from a variational autoencoder with encoder `enc` and decoder `dec`. Which piece of code needs to be inserted at the marked location to complete the code?

```python

# Compute means and standard deviations in the
# latent space
Mu, Sigma = enc(X)

# Sample in the latent space
# TODO: Marked Location

X_reconstructed = dec(Z)
```
