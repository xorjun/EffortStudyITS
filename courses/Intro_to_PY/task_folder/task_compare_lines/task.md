# Comparing two lines

You can also use the `plot` function to draw multiple lines into the same graph. And you can use the `legend` function to label the different plots. For example:

```python

import matplotlib.pyplot as plt

plt.plot([1, 2, 3], [2, 3, 5])
plt.plot([1, 2, 3], [3, 2, 1])
plt.legend(['line 1', 'line 2'])
plt.show()
```

yields the graph:

![Two lines. The first goes through the points (1, 2), (2, 3), and (3, 5), which is increasing. The second goes through the points (1, 3), (2, 2) and (3, 1) and is linearly decreasing. The two lines intersect at (1.5, 2.5)](lines.png)

## TODO

Create three plots in the same graph, one for the function $f(x) = x$, one for the function $f(x) = x^2$ and one for the function $f(x) = exp(x)$ for $x \in [0, 0.1, ..., 2]$. Label your plots.
