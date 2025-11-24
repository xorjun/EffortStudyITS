# Importing Modules in Python

## Modules

Modules in Python are files containing Python code, functions, and variables that can be reused in other Python scripts or programs. 
They allow you to organize your code into separate files, making it more modular and maintainable. Modules help avoid code duplication and promote code reuse.

Python also provides some standard modules that can be imported to gain access to additional functions. For example:

```python
import math   # Import the module 'math'
math.sqrt(25)  # Call a function from the module (in this case function 'sqrt' from the module 'math')
```
will yield the square root of 25:
```
5
```

In the tutoring system, all modules are installed and imported for you, but please be aware that for coding outside the ITS you would have to install and call them before using!

## TODO

Create a function that finds the largest perfect square (a number that is a square of an integer) in a list of numbers and returns it. If no perfect square is found, the function should return `None`. 

```python
def largest_perfect_square(numbers):
    ...
```