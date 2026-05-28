# Wilcoxon signed rank test usage

**Note:** This task is related to Bonus Task 01.17 from the first exercise sheet.

Assume you have four arrays available:

1. `pre_test_control`
2. `pre_test_intervention`
3. `post_test_control`, and
4. `post_test_intervention`

containing the data recorded during a study, namely 1) the pre-test results in the control group, 2) the pre-test results in the intervention group, 3) the post-test results in the control group, and 4) the post-test results in the intervention group.

## TODO

Write a python function that performs two Wilcoxon sign rank tests (using the function [scipy.stats.wilcoxon](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html)): the first test should check whether the post-test scores in the control condition are significantly different from the pre-test score; the second test should check the same for the intervention condition. The function should return the p-values of both tests.