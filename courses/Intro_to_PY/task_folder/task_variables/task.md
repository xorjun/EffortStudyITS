# Variable Types

## Multiple Return Values

In Python, a function can also return several values:

```python
# Function with a return value
def functionWithRetVals(x,y):
    return x + 3, y + 6
r = functionWithRetVals(5,1)
print(r)

```

will print a tuple of two outputs:

```
(8, 7)
```

## Types of variables: type()

The special `type` function returns the type of a variable.

```python
c = 2.5
print(c)
print(type(c))
```

will yield the output:

```
2.5
<class 'float'>
```

and:

```python
d = True
print(d)
print(type(d))
```

will yield the output:

```
True
<class 'bool'>
```

## Typecasting

In Python, you can also change the type of variable through casting. For example:

```python
y = str(3)
print(y)
print(type(y))
```

will yield the output:

```
3
<class 'str'>
```

## To Do

Write a function, that for each input integer `n` returns `n` as three new types: as string, as integer, and as float.