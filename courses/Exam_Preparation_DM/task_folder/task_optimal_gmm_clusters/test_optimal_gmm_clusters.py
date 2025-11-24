from example_solution import optimal_gmm_clusters
#!cut_imports!#

def test_optimal_gmm_clusters():
    from sklearn import datasets
    import numpy as np
    from sklearn.mixture import GaussianMixture
    # Load the Iris dataset
    iris = datasets.load_iris()
    X = iris.data
    y = iris.target

    res = optimal_gmm_clusters(X)

    #Data Type
    assert type(res) in [int, np.int_], "Return type hould be an integer specifying the optimal number of clusters."

    #Iris result
    assert res in [2, 3], f"Optimal clusters for the iris dataset should be 2 or 3 but are, {res}"

    # Results for a random Gaussian Mixture
    n_components = 2
    means = np.array([[1, 1], [5, 5]])
    covariances = np.array([[[1, 0.5], [0.5, 1]], [[1, -0.5], [-0.5, 1]]])
    weights = np.array([0.6, 0.4])  # Relative weight of each component

    gmm = GaussianMixture(n_components=n_components)
    gmm.covariances_ = covariances
    gmm.weights_ = weights
    gmm.means_ = means
    random_sample, _ = gmm.sample(200)  # The second return value is the component index for each sample

    res = optimal_gmm_clusters(random_sample)
    assert res == 2, f"Optimal clusters for a random dataset of {n_components} gaussian-mixtures should be {n_components}, not {res}"