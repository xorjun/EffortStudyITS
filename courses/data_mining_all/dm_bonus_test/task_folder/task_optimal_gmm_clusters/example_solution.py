#!function!#
import numpy as np
from sklearn.mixture import GaussianMixture
import random

random.seed(42)
def optimal_gmm_clusters(X, max_clusters=10):

#!prefix!#

    """
    Determine the optimal number of clusters using Gaussian Mixture Models.

    Parameters:
    - data: Input data for clustering.
    - max_clusters: Maximum number of clusters to consider.

    Returns:
    - best_n_components: Optimal number of clusters.
    """

    # Fit Gaussian Mixture Models for different numbers of components
    n_components = np.arange(1, max_clusters + 1)
    models = [GaussianMixture(n, random_state=0).fit(X) for n in n_components]

    # Get BIC values
    bic_values = [model.bic(X) for model in models]

    # Determine the optimal number of clusters based on BIC
    best_n_components_bic = n_components[np.argmin(bic_values)]

    # Return the optimal number of components based on BIC
    return best_n_components_bic
