# nDCG

Consider a recommendation list  $ r \in \mathbb{N}^n $ where entries $ r_i $ represent the relevance of item $ i $ to the user. Normalized Discounted Cumulative Gain (nDCG) is a metric used to evaluate the ranking quality of a recommendation list. $ rel_i $ is based on the numerical rating of the item.  

That is, as an input you may receive: 

```python
relevance = [3, 2, 1, 4, 0, 5]  # Evaluation of the recommender's prediction by a user
```

This means, that the ideal case would be: 

```python
ideal_recommendation = [5, 4, 3, 2, 1, 0]  # Ideal recommendation order
```

Among others, this is a metric very commonly used to evaluate the quality of a recommender system. 
In this task, please write a function for computing the nDCG of a recommendation list @k: that is, you only have to evaluate the quality of the recommendations on the first k positions in the list.