# Welcome

Welcome to this collection of bonus tasks for "Introduction to Data Mining"!

Before starting here, we strongly encourage to participate in a **pre-test** of your data mining knowledge and a **Learning Personality Survey**. You can find both of these in the course overview when you click on the 'House' symbol on the top left.

Now, let us start with **probability theory**.

## Bayes' theorem

Recall Bayes' theorem: If we have two random variables $X$ and $Y$, the conditional probability distribution $P_{Y|X}$ can be computed using the formula

$$P_{Y|X}(y|x) = \frac{P_{X|Y}(x|y) \cdot P_Y(y)}{P_X(x)}$$

and the marginal $P_X(x)$ can be obtained via the law of total probability:

$$P_X(x) = \sum_y P_{X|Y}(x|y) \cdot P_Y(y)$$

Now, assume we have two discrete random variables $X$ and $Y$ with the domains $\{0, \ldots, m\}$ and $\{0, \ldots, n\}$, respectively.

## TODO

Write a function `bayes` with two input arguments: A matrix `P_XY` where `P_XY[i, j]` is the conditional probability $P_{X|Y}(i|j)$, and a vector `P_Y` where `P_Y[j]` is the marginal $P_Y(j)$. The output of your function should be a matrix `P_YX` where `P_YX[j, i]` is the conditional probability $P_{Y|X}(j|i)$.