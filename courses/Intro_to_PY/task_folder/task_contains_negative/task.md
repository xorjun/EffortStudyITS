# Logical operations

Python provides a wide range of logical operations to process truth values (aka Boolean values) in an intuitive fashion. For example:

```python
c = True

not_c = not c
print(not_c)

c_test = c is False
print(c_test)

c_test2 = not_c is not True
print(c_test2)

l = True and False
print(l)

print(True or False)
```

yields the output:

```
False
False
True
False
True
```

When operating on lists of truth values, the `any` operator is particularly interesting:


```python
print(any([True, False, False, True, False]))
print(any([False, False, False, True, False]))
print(any([False, False, False, False, False]))

```

yields the output:

```
True
True
False
```

## To Do

Create a function that checks if a given list of numbers contains any negative numbers. The function should return True if there are any negative numbers and False, otherwise.

```python
def contains_negative(numbers):
    ...
```
