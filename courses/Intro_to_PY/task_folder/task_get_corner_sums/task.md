# Entries and indexation 

Similar to lists, matrices can be accessed with indexing and slicing operations. For example:

```python

my_matrix = np.array([[1, 2], [3, 4]])  # Create a new 2x2 matrix

print(my_matrix)
print(my_matrix.shape)

# Access entries
print(my_matrix[0,0])
print(my_matrix[0,1])
# Slicing
print(my_matrix[0,:])  # First row
print(my_matrix[:, 0]) # First column
print(my_matrix[:, 1])  # Second column
```

will yield the output:

```
[[1 2]
 [3 4]]
(2, 2)
1
2
[1 2]
[1 3]
[2 4]
```

## To Do 

Write a function that receives two matrices as input and returns two outputs: the sum of the elements in the left bottom corner of both matrices, and the sum of the elements in the top right corner of both matrices.
 
```python
def get_corner_sums(array1, array2):
    ...
```