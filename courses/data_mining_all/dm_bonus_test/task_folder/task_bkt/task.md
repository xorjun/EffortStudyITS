# Bayesian Knowledge Tracing

Write a function that implements the inference of Bayesian knowledge tracing.

The input of your function is an array `x` of successes (1) and failures (0) of a student on a skill, as well as a BKT model, specified by the parameters `pstart`, `pslip`, `pguess`, and `ptrans`.

Your output should be an array `p`, where `p[t]` is the probability that the student has mastered the skill at time step `t+1`, conditioned on the data `x[:t+1]`.
