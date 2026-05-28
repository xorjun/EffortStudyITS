# Independence

Assume we have two discrete random variables $X$ and $Y$ with the domains $\{0, \ldots, m\}$ and $\{0, \ldots, n\}$, respectively.

Write a function `independence`. The input is a matrix `P_XY` where `P_XY[i, j]` is the joint probability $P_{X, Y}(i, j)$. The output should be `True` if X and Y are independent and `False` if they are not.