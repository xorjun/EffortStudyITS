# nDCG at k

Assume a recommender system ranks `N` items. For the recommendation, we are given an array `relevance` where `relevance[i]` indicates the relevance of the item at rank `i` to the user. 

That is, as an input you may receive: 

```python
relevance = [3, 2, 1, 4, 0, 5]  # Evaluation of the recommender's prediction by a user
```

Implement a function that computes the _normalized Discounted Cumulative Gain (nDCG) at k_ for such an input relevance array.

Recall that the DCG is defined as

$\text{DCG} = \sum_{i=1}^N \frac{r_i}{\log_2(i+1)}$

and the nDCG is the DCG for the input ranking list divided by the ideal DCG that could be obtained for these relevances.

The nDCG at k means that you should only consider the first k ranks.

**Hint:** Note that the ideal ranking can also use data after position k in the input relevance array.

