# Linear algebra

The NumPy linear algebra module (`numpy.linalg`) provides efficient low level implementations of standard linear algebra algorithms. 
For example, in you can solve systems of linear equations. The system

2x + 3y = 1  
3x + 4y = 1

can be solved via the code:

```python 
import numpy as np

a = np.array([[2, 3], [3, 4]])

b = np.array([1, 1])

x = np.linalg.solve(a, b)

print(x)
```

which yields the output:

```
[-1.  1.]
```

## TODO

Write a function that receives a matrix as input, sets all values except the diagonal to zero and then returns the eigenvalues and eigenvectors of the new diagonal matrix (**np.linalg.eig()** is worth checking out).

Please use the following format:

```python
def eigen_of_diagonal(matrix):
    ...
```