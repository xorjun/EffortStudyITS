from random import randrange

sub_domains = ["Statistical Testing", "Clustering", "IRT and KT", "Recommenders", "Deep Models"]
curriculum = [["mean_and_std","pooled_variance", "nll_functions", "pearson", "wilcoxon"], 
              ["pca_fa", "optimal_gmm_clusters", "gmm_vs_kmeans"], 
              ["IRT_logreg", "param1_2", "bkt", "case_kt"], 
              ["user_similarity", "ndcg_at_k", "bias_rs"], 
              ["markov_models", "deep_learning","critical_thinking"]]
course_options = [[0,1,2,3,4],
                  [0,1,3,2,4], 
                  [0,2,1,3,4], 
                  [0,2,3,1,4], 
                  [0,3,1,2,4], 
                  [0,3,2,1,4]]

rand_subdomain_order = -1

if rand_subdomain_order == -1:
    rand_subdomain_order = randrange(len(sub_domains))

rand_chosen_option = course_options[rand_subdomain_order]

sorted_curriculum = [subdomain_tasks for _, subdomain_tasks in sorted(zip(rand_chosen_option, curriculum))]

curriculum = [item for sublist in sorted_curriculum for item in sublist]

print(f"rand_subdomain_order: {rand_subdomain_order}")
print(f"rand_chosen_option: {rand_chosen_option}")
print(f"curriculum: {curriculum}")

# rand_subdomain_order: 3
# rand_chosen_option: [0, 2, 3, 1, 4]
# adj_curriculum: ['mean_and_std', 'pooled_variance', 'nll_functions', 'pearson', 'wilcoxon', 
#                  'user_similarity', 'ndcg_at_k', 'bias_rs', 
#                  'pca_fa', 'optimal_gmm_clusters', 'gmm_vs_kmeans', 
#                  'IRT_logreg', 'param1_2', 'bkt', 'case_kt', 
#                  'markov_models', 'deep_learning', 'critical_thinking']