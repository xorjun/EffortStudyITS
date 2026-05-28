# Create a Function

Programs often repeat actions.

Instead of writing the same code many times, Python allows us to organize code into small reusable parts.

These reusable parts are called **functions**.

A function is a block of code that can run later.

Python uses the word `def` to create a function.

---

## Understanding Function Structure

```python
def say_hello():
    print("Hello")
```

Let's look at the parts:

- `def` tells Python we are creating a function
- `say_hello` is the function name
- `()` is required after the function name
- `:` tells Python the function code starts below
- the indented line belongs to the function

---

## Understanding Indentation

The spaces before a line are called **indentation**.

Indentation is very important in Python.

Indented lines belong to the function.

```python
def say_hello():
    print("Hello")
```

The `print` statement is indented, so Python knows it belongs to the function.

---

## Calling a Function

Creating a function does not automatically run it.

The function only runs when it is **called**.

```python
def say_hello():
    print("Hello")

say_hello()
```

Console output:

```
Hello
```

The last line `say_hello()` calls the function.

---

## Important Notes

- functions help organize code
- functions can be reused later
- indentation is required in Python
- functions only run after being called

---

## To Do

Complete the missing part below so the function runs and prints:

```
Welcome to Activity Tracker
```
