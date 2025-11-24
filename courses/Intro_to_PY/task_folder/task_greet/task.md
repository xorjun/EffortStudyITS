# Welcome!

## Before you start

It is pleasure to welcome you to our Intelligent Tutoring System! While we hope that you will have a great experience with it, we would also like to mention that 
this ITS is in its alpha stage, so not all the intended functionality is yet available. 

You can find more on this tutoring system in "About". 

## This is the very beginning of the Introduction to Python

This is a short introduction to the Python programming language. It focuses on usage and not on theory or underlying concepts. The content is chosen in order to **prepare you for any subsequent programming exercises**.

**This is a small crash course for computer scientists who have already learned anothe rprogramming language. It is NOT a complete introduction to the Python programming language.**

If you want to dive deeper, here is some additional material:
- [https://docs.python.org/3/tutorial/index.html](https://docs.python.org/3/tutorial/index.html)
- [https://cs231n.github.io/python-numpy-tutorial/](https://cs231n.github.io/python-numpy-tutorial/)
- [https://matplotlib.org/users/pyplot_tutorial.html](https://matplotlib.org/users/pyplot_tutorial.html)

## Strings

We start by processing **strings**. A string is, basically, a piece of text, usually written in double quotes, like `"This is a string."`

There are multiple ways of manipulating strings in python. The most easy one is the "+" operator for string concatenation. There is also the option to use a format string via the format method. The most recommended method is to use f-strings, as they are the most readable and require the least boilerplate code. 

```python
name = "Alice"
# Concatenation via +
"Hello" + name
# Format method
"Hello {0}".format(name)
# f-string
f"Hello {name}"
```

The command `print` can be used to print out a string. For example: 

```python
print("Who is "+"Marla"+"?")
print( 5 + 5 )
```

will output:

```
Who is Marla?
10
```

## To Do

Write a function named `greet` that prints `"Hello {name}"` where `name` is taken as the function parameter. 

Afterwards, call your function two times to greet `Alice` and `Bob`.

**Note:** Python uses a fixed indentation for separating blocks. You may be already familiar to other programming langauges like JAVA which usually use curly brackets for this purpose. However, Python programs require you to always indent your blocks by either four spaces or a TAB.