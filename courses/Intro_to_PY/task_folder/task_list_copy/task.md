# Lists 3

## References and copies

Primitive types in Python are *passed by value*, meaning that every new variable automatically creates a copy. For example:

```python

a = 2
b = a
b = 3
print(a)
print(b)
```

yields the output

```
2
3
```

However, lists in Python are *passed by reference*, meaning that you can (accidentally) change the content of another variable without noticing. For example:

```python

a = [2]
b = a
b[0] = 3
print(a)
print(b)
```

yields the output

```
[3]
[3]
```

meaning that both `a` and `b` refer to the same list.

If you want to create a copy, you need to do that explicitly, using the `copy` function:

```python

a = [2]
b = a.copy()
b[0] = 3
print(a)
print(b)
```

yields the output

```
[2]
[3]
```


## To Do 

Define a function

```python
def list_copy(my_list):
    ...
```

which takes a list as input and creates a new list with the first and last elements of the original list removed (without changing the original list). Return both the new list and the old list.

**Note:** Make sure that you handle the special cases of an empty list and a one-element list.