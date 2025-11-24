'''
#!json!#
{
    "possible_choices": ["PCA aims to transform the original variables into a new set of uncorrelated variables called principal components.",  
                         "Similarly to PCA, FA assumes that the observed variables are influenced by common factors",  
                         "Both PCA and FA aim to find interpretaple underlying patterns within the data.",
                         "Principal components are orthogonal to each other.",
                         "FA without encorporated error terms is just PCA.",
                         "The main goal of the FA is to reduce dimensionality of the data."],
    "correct_choices": [true, false, false, true, true, false],
    "choice_explanations": ["This statement is correct. PCA indeed tries to do so. These components are linear combinations of the original variables and capture the maximum variance in the data.", 
                            "This statement is not correct. FA assumes that the observed variables are influenced by both common for all and unique factors, which allows for correlations.", 
                            "This statement is not correct. PCA and FA both can find interpretable, but this is not a necessity for the PCA, while the factors found through FA are intended to have a meaningful interpretation.",
                            "This statement is correct. Principal components are orthogonal to each other, meaning they are uncorrelated.",
                            "This statement is correct. The absence of the error term in FA renders it to be a deterministic model, equal to PCA in its nature.",
                            "This statement is not correct. This is the goal of PCA, while FA looks to understand the connection between latent factors."]
}
#!json!#
'''