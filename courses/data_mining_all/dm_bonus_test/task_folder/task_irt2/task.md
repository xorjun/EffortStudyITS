# 2-Parameter IRT

**Note:** This task is related to Bonus Task 03.14 from the third exercise sheet.

Recall the equation for a 2-parameter IRT model:

$$p_{X|A, B,\Theta}(1|b,\theta) = \frac{1}{1 + \exp[-a \cdot (\theta-b)]}.$$

Write a python function that takes student abilities and their answers for a task as input and returns the a and b parameter for this task. You should use Logistic Regression for this with L2 regularization and $C = 1$.


