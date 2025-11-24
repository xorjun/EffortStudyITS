# Numpy

The numpy module provides a lot of utility functions to process arrays and matrices of numbers, especially for linear algebra. As such, numpy is crucial for data science and machine learning.

## Creating arrays in numpy

Numpy contains several ways to construct arrays. For example, the code:

```python
import numpy as np

my_vector = np.array([1, 2, 3])  # Create a new vector with 3 elements (3d)

print(my_vector)
print(type(my_vector))
print(my_vector.shape)
```

yields the output:

```
[1 2 3]
<class 'numpy.ndarray'>
(3,)
```

And the code:

```python
np.zeros(5)  # Note: Shape must be specified as a tuple!
```

yields the output:

```
array([0., 0., 0., 0., 0.])
```

## TODO

Write a function that receives an integer `n` as input and produces three outputs:

1. An array of zeros of the size *n*.
2. An array of ones of the size *n*.
3. An array of fives of the size *n*.

If `n` is zero or negative, the function should return `None`.