# Collaborative filtering

Collaborative filtering is a popular approach in recommender systems where the similarity between users is used to make recommendations. 
The way you calculate user similarity can vary based on whether you are dealing with explicit or implicit feedback.
At the lectures, we discussed the use of Pearson similarity for the explicit feedback and cosine similarity for the implicit.
However, both similarity metrics can be used in both cases. 

Let input of a function be a rating matrix (users as rows, items as columns) and type of feedback ("explicit" or "implicit").
Build a function, that will be calculating the similarity of the 2 given users within the rating matrix, using a respective type of similarity measure. 
You may use "cosine" distance from the scipy package. 

Please note, that missing values in rating matrix are usually shown with "0", and the similarity should be calculated on the set of mutually observed items. Otherwise it should be 0. 