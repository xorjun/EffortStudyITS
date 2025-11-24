# Print Name

There are multiple ways of manipulating strings in python. The most easy one is the "+" operator for string concatenation. There is also the option to use a format string via the format method. The most recommended method is to use f-strings, as they are the most readible and require the least boilerplate code. 

```python
name = "Alice"
# Concatenation via +
"Hallo" + name
# Format method
"Hallo {0}".format(name)
# f-string
f"Hallo {name}"
```

Write a function named greet that prints "Hello {name}" where name is taken as the function parameter. Use the following signature:

```python
def greet(name):
    ...
```

Use greet to print welcome slogans to Alice and Bob, such that your program ouputs.

```
Hello Alice
Hello Bob
```