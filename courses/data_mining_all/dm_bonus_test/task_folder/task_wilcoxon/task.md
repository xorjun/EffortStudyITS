# Wilcoxon signed rank test

Write a python function that receives as input two arrays `x` and `y` and returns the test statistic of the Wilcoxon signed rank test.

This test statistic is the signed sum of ranks for the absolute differences, meaning: You have to compute the differences `x[i] - y[i]`, take the absolute values, rank the differences and then sum the ranks - but the ranks for negative differences get a minus.

So, for example, for the input arrays `[1, 2]` and `[2, 0]` the differences would be `[-1, 2]`. The ranks for the absolute values would be `[1, 2]`, and the test statistic would be `-1 + 2 = 1`.
