'''
#!json!#
{
    "possible_choices": ["GMM assumes the clusters to be similar in shape. ",  
                         "Both GMM and K-means methods are quite sensitive to the inital parameters, so that the clusters would change based on it. ",  
                         "Kmeans is more computationally efficient than GMM.",
                         "Kmeans performs a hard cluster assignment, while GMM has a soft one.",
                         "GMM converges to solution more quickly than Kmeans. ",
                         "All three methods require the number of clusters to be specified in advance.",
                         "Agglomerative clustering does not need specific assumptions about the data, compared to the other two methods",
                         "Out of the three, K-Means is best at handling the outliers."
                        ],
    "correct_choices": [false, false, true, true, false, true, true, false],
    "choice_explanations": ["This statement is not correct. Due to its probabilitstic nature, the GMM allows clusters tohave different shapes, sizes, and orientations.", 
                            "This statement is not correct. Kmeans is much more sensitive to the initialization (of centroids) than GMM, because of its deterministic cluster assignment.", 
                            "This statement is correct. GMM required estimation and update of many more parameters than Kmeans, which makes it less computationally efficient.",
                            "This statement is correct. At each step, the Kmeans assigns each point strictly to 1 cluster, while GMM give a probabilistic distribution of the assignment.",
                            "This statement is not correct. KNN is computationally more efficient and converges to the solution more quickly.",
                            "This statement is correct. Knowing the number of clusters is crucial for introducing the criterion to end clustering process.",
                            "This statement is correct. Agglomerative clustering can handle the clusters with arbitrary form.",
                            "This statement is not correct. Agglomerative clustering is best at hadnling the outliers, they will just be connected last."
                            ]
}
#!json!#
'''