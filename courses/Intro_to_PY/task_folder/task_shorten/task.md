# Lists 1

Lists are ordered collections of data that can be changed after creation. In Python, lists are denoted with square brackets. As with tuples, the entries of lists can be accessed with square brackets and slice operators. For example:

```python
a = [1,2,3,1,4,5,6]
print(type(a))

# Indexing operator with positive values
print(a[0])  # First item
print(a[1])  # Second item

# Indexing with slicing
print(a[1:])

# with negative values
print(a[-1])  # Last item
print(a[-2])  # Item before last item
print(a[-3])  # ...
```

will yield the output

```
list
1
2
[2, 3, 1, 4, 5, 6]
6
5
4
```

## If control structure

To handle special cases, we often need code that only gets executed in this special case. For that, Python provides the `if` control structure. For example:

```python

def my_fun(n):
    if n < 0:
        print(f'{n} is negative')
    elif n == 0:
        print(f'{n} is zero')
    else:
        print(f'{n} is positive')

my_fun(-3)
my_fun(0)
my_fun(24)
```

will yield the output

```
-3 is negative
0 is zero
24 is positive
```

## To Do

Define a function that takes a list as input and returns a new list, containing only the first and the last value of the input list.

**Note:** For a list of length one, the first element is cinsidered the same as the last element. Make sure that you handle the special cases of the empty list and a one-element list.
