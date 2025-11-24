# Wilcoxon signed rank test usage

**Note:** This task is related to Bonus Task 01.17 from the first exercise sheet.

Assume you have four arrays available: `pre_test_control`, `pre_test_intervention`, `post_test_control`, and `post_test_intervention` containing the data recorded during a study, namely the pre-test results in the control group, the pre-test results in the intervention group, the post-test results in the control group, and the post-test results in the intervention group.

## TODO

Write a python function that performs two Wilcoxon sign rank tests (using the function `scipy.stats.wilcoxon`): the first test should check whether the post-test scores in the control condition are significantly different from the pre-test score; the second test should check the same for the intervention condition. The function should return the p-values of both tests.