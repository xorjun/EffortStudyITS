# Factorial

The factorial function is defined as the product of all positive integers less or equal to a given positive integer $n$: 

$$n! := \prod_{i=1}^n i$$

## Raise Operator

Note that the factorial is not defined for negative numbers. You can raise an Exception with the "raise" keyword to account for this. For example:

```python
raise ValueError('I got a negative number')
```

will yield the exception:

```
Traceback (most recent call last):
  File "<python-input-2>", line 1, in <module>
    raise ValueError('I got a negative number')
ValueError: I got a negative number
```

## TODO

Implement the factorial function in Python. Throw an exception for negative inputs or if the input is not an integer.

```python
def factorial(n):
    ...
```