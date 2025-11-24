from example_solution import agglomerative_clustering
#!cut_imports!#
def test_agglomerative_clustering():
    import numpy as np
    # Generate synthetic 2D data with three clusters
    np.random.seed(42)

    # First cluster around (2, 2)
    cluster1 = np.random.normal(loc=[2, 2], scale=0.5, size=(20, 2))

    # Second cluster around (6, 6)
    cluster2 = np.random.normal(loc=[6, 6], scale=0.5, size=(20, 2))

    # Third cluster around (10, 2)
    cluster3 = np.random.normal(loc=[10, 2], scale=0.5, size=(20, 2))

    # Concatenate the clusters to form the dataset
    your_data = np.concatenate([cluster1, cluster2, cluster3])

    # Example Usage
    clusters = agglomerative_clustering(your_data)

    #Output Data Type
    assert type(clusters) == list, "The outputted Clusters should be a nested list of numpy arrays or tuples which each describe a point"

    #Output type 2
    assert len(clusters)==1, f"There should only be one top-level cluster, in your solution there are {len(clusters)}"

    #Full Solution 1
    data = np.array([(1,1),
                    (3,3),
                    (4,4),
                    (1,2)])
    true_res = [[[np.array((1,1)),np.array((1,2))], [np.array((3,3)), np.array((4,4))]]]
    clusters = agglomerative_clustering(data)
    assert str(clusters)==str(true_res), f"For a small dataset your output did not match the desired result,\ninput:\n{data}\noutput: {clusters}\ndesired output: {true_res}"

    #Full Solution 2
    data = np.array([(10,10),
                    (12,11),
                    (100,100),
                    (10000,10000)])
    true_res = [[[[np.array((10,10)), np.array((12,11))], np.array((100,100))], np.array((10000,10000))]]
    clusters = agglomerative_clustering(data)
    assert str(clusters)==str(true_res), f"For the second small dataset your output did not match the desired result. {clusters}"
