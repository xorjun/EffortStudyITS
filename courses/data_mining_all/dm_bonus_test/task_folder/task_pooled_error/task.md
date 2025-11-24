# Pooled Standard Error for Welch's t-test

To handle statistical testing for samples of different variance, one needs to pool the variances of both samples.

Implement a function that receives as input two arrays `x` and `y` and returns the pooled standard error of both arrays based on the equation for Welch's t-test. The pooled standard deviation is given by the following equation (taken from the lecture slides):

$$ \tilde \sigma = \sqrt{\frac{\sigma_x^2}{n_x} + \frac{\sigma_y^2}{n_y}} $$
