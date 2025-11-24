# Comments and Tuples

## Comments

You can use one-line or multi-line comments. 
```python
# This is a one-line comment

'''
I am a multi line comment
bla bla
bla
'''

```

Note that the multi-line comment is technically a string. But because it is not assigned to any variable, it does not influence the code in any way.

## Tuples

A tuple is an ordered collection of data that is *unchangeable*. A tuple is denoted with brackets in Python. You can access entries of the tuple with square brackets. For example:

```python
# NOTE: A tuple is in round parantheses.
t = (1,2,3)  # NOTE: A tuple is immutable (=> can not be changed after it's created)
print(t)
print(t[0])
print(t[1])
```

would return the output

```
(1, 2, 3)
1
2
```

Python also provides a **slicing** operator to access multiple entries of a tuple at the same time. For example:

```python
# Slicing tuples
my_tuple =(1,2,3,4,5)
print(my_tuple[2:]) #Print elements from index 2 to end 
```

yields the output:

```
(3, 4, 5)
```

You can **unpack** a tuple by assigning each entry to a separate variable. For example:

```python
t = (1,2,3)
# Unpack a tuple
a, b, c = t

print(a)
print(b)
print(c)
```

would yield the output:

```
1
2
3
```

## The 'in' keyword

The `in` can be used to check if something is contained in a tuple. For example:

```python
t = (1, 2, 3)
print(1 in t)
print(4 in t)
```

would yield the output:

```
True
False
```

## Typecasting into tuples

Similarly to previous exercise, you can typecast variables into tuples. For example:

```python
a = 'ITS'
print(tuple(a))
```

would yield the output:

```
('I', 'T', 'S')
```

## To Do

Create a function that takes a string for a name as input and returns two outputs:
1. Whether the name contains an `x` or an `X` (`True` or `False`).
2. A tuple containing all but the first letters in the name.

For example, the desired output for the name `"Riza"` would be:
```
False, ('i', 'z', 'a')
```