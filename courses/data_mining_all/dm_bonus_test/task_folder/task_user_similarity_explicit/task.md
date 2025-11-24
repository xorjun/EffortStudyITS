# Collaborative filtering: Explicit Case

Collaborative filtering is a popular approach in recommender systems where the similarity between users is used to make recommendations. Depending on your data set, different similarity measures may be suitable. In this task, we will consider the Pearson correlation as similarity measure.

## ToDo: 

Write a function that receives as input two rows of a rating matrix `x` and `y`, where missing data is indicated as `np.nan`. Your function should return the Pearson correlation between both arrays, disregarding missing data.

More specifically, the means should be computed separately for each array, and for the similarity you should consider only the entries where both arrays are not `np.nan`.
