# Defining own functions

## def

In the previous exercise, you have already used the `print` function and defined your own function with `def`. 

```python
# A very simple function
def myFunction():
    print("Hello from inside myFunction!")
myFunction()
```

will yield the output:

```
Hello from inside myFunction!
```

Your function can be either called by itself (as in the example above), or it can have some arguments: 

```python
# A simple function with arguments
def anotherFunction(a, b, c):
    print(a)
 anotherFunction(89, 4, 2)   
```

will yield the output:

```
89
```

Additionally, a function can return a value:

```python
# Function with a return value
def functionWithRetVal(x):
    return x + 1
r = functionWithRetVal(5)
print(r)

```

will yield the output:

```
6
```

## To Do 

Define a function that receives a real number as input and returns the square of this number.
Use the folowing signature:

```python
def square(x):
    ...
```

**Note:** [Click here](https://www.w3schools.com/python/gloss_python_arithmetic_operators.asp) for a list of arithmetic operators in Python. 