# Performance Factors Analysis with Difficulty Parameters

**Note:** This task is related to Bonus Task 03.15 from the third exercise sheet.

Write a Python function `pfa_extended` that uses LogisticRegression to train a PFA model with difficulty parameters for each task. In particular, the input of your function should be:


Your input consists of
- a numpy array `X` of shape $T \times 2$ which represents the data of a single student who attempted `T` tasks. The first column are the task indices (from 0 to n-1, where n is the number of tasks), and the second column are 0 or 1, depending on whether the student was successful or not.
- a matrix `Q` of shape $n \times K$, where $n$ is the number of tasks and $K$ is the number of skills. `Q[j, k] = 1` if task $j$ needs skill $k$ and `Q[j, k] = 0`, otherwise.

The logit of the model for student $i$ and task $j$ should be:

$$\text{logit} = b_j + \sum_{k=1}^K q_{k, j} \cdot (\gamma_k \cdot s_{i, k} + \rho_k \cdot f_{i, k} + \beta_k)$$

where $b_j$ is the difficulty parameter for task $j$, $\gamma_k$ is the parameter for the learning rate from successes for skill $k$, $s_{i, k}$ are the past successes of student $i$ in skill $k$, $\rho_k$ is the parameter for the learning rate from failures skill $k$, $f_{i, k}$ are the past failures of student $i$ in skill $k$, and $\beta_k$ is the baseline skill parameter for skill $k$.

The outputs of your function should be
- a numpy array `gamma` containing the $K$ gamma parameters, one per skill
- a numpy array `rho` containing the $K$ rho parametes, one per skill
- a numpy array `beta` containing the $K$ beta parameters, one per skill
- a numpy array `b` containing the $n$ difficulty parameters, one per task.

You should use Logistic Regression for this with L2 regularization and $C = 10$.

**Hint:** You need to re-format the input into valid input for logistic regression.