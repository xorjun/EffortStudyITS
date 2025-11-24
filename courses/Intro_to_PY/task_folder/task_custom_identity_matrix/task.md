# Matrices

Numpy is particularly useful for handling matrices, meaning two-dimensional arrays. Numpy provides plenty of useful functions to create matrices. For example:

```python
import numpy as np 
print(np.eye(3)) # 'eye' is a play on words
# and refers to the identity (or 'eye'-dentity) matrix
np.zeros((5,3))  # Note: Shape must be specified as a tuple!
```

will create the output:

```
[[1. 0. 0.]
 [0. 1. 0.]
 [0. 0. 1.]]

array([[0., 0., 0.],
       [0., 0., 0.],
       [0., 0., 0.],
       [0., 0., 0.],
       [0., 0., 0.]])
```

 ## TODO

Create a function that generates a square diagonal matrix of size `n` where all diagonal elements are set to `value`.

```python
def custom_identity_matrix(n, value):
    ...
```

If the matrix cannot be created ($n\leq 0$), return None. 