# Bar plots

With `matplotlib.pyplot.bar` function, you can create bar plots. It gets x and y coordinates, just as before, but the result looks different:

```python

import matplotlib.pyplot as plt

plt.bar([1, 2, 3], [2, 3, 5])
plt.show()
```

creates the following graph:

![A plot with three bars, one with height 2, one with height 3, one with height 5.](bars1.png)

For such plots, we typically want to give each bar a name. We can change the labels on the x axis with the `xticks` function like this:

```python

import matplotlib.pyplot as plt

plt.bar([1, 2, 3], [2, 3, 5])
plt.xticks([1, 2, 3], ['bar 1', 'bar 2', 'bar 3'])
plt.show()
```

which creates the following graph:

![The same graph as before but the three bars are labeled with "bar 1", "bar 2", and "bar 3" on the x axis.](bars2.png)

Finally, we often want to draw lines to indicate how much the data spreads around the height of the bar. For that, we can use the `yerr` argument of the `bar` function. It takes a list of spread values, one for each bar.

```python

import matplotlib.pyplot as plt

plt.bar([1, 2, 3], [2, 3, 5], yerr = [0.1, 0.2, 0.1])
plt.xticks([1, 2, 3], ['bar 1', 'bar 2', 'bar 3'])
plt.show()
```

which creates the following graph:

![The same graph as before but the three bars are now shown with a small black line which spreads 0.1 around the height of the first bar, 0.2 around the height of the second, and 0.1 around the hight of the third.](bars3.png)

## TODO

Create a plot with two bars. The first bar should show the mean value (with `yerr` showing standard deviation) of the numbers `[1, 3, 2, 3, 2, 3, 2]`, the second bar should show the mean value (with `yerr` showing standard deviation) for the numbers `[3, 2, 1, 2, 3, 2, 1]`. Label the bars as `"data 1"` and `"data 2"` on the x axis.

**Hint:** You are allowed to use the functions `np.mean` and `np.std` to compute mean and standard deviation of numbers in a list.
