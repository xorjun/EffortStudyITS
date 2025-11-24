# Performance Factors Analysis

Write a python function `pfa_inference` that returns the estimated skill by a given PFA model for a given student performance.

Your input consists of
- a numpy array `X` of shape `(T, 2)` which represents the data of a single student who attempted `T` tasks. The first column are the task indices (from 0 to n-1, where n is the number of tasks), and the second column are 0 or 1, depending on whether the student was successful or not.
- a matrix `Q` of shape $n \times K$, where $n$ is the number of tasks and $K$ is the number of skills. `Q[j, k] = 1` if task $j$ needs skill $k$ and `Q[j, k] = 0`, otherwise.
- an array `beta` of shape $K$ where `beta[k]` is the baseline skill for skill `k` according to the PFA model
- an array `gamma` of shape $K$ where `gamma[k]` is the skill acquired per success for skill `k` according to the PFA model
- an array `rho` of shape $K$ where `rho[k]` is the skill acquired per failure for skill `k` according to the PFA model

The output of your function should be a numpy array `Theta` of shape `(T, K)`. `Theta[t, k]` should be the amount of skill the student has at time `t` in skill `k` according to the PFA model.
