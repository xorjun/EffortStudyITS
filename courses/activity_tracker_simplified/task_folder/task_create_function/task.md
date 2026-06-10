# Task 2 — Create a Function

## Learning Content

Programs often repeat actions.

Instead of writing the same code many times, we can organize code into small reusable parts.

These reusable parts are called **functions**.

A function is a block of code we can re-use later.

To tell the computer we are starting a function, we use the code word:

```python
def
```

---

## Understanding Function Structure

Example:

```python
def showFruit():
    print("Apple")
    print("Banana")
```

Let's look at the parts:

- `def` tells the computer that we are creating a function.
- `showFruit` is the function name. The name can be any set of words, as long as they are not separated by whitespaces. Here, we use `show` and `Fruit`, and put them together.
- `()` is required after the function name. We can regard it as part of the name for now.
- `:` tells the computer the function code starts below.
- The spaces before a line are called **indentation**. The indent is important, as it tells the computer that the lines still belong to the function.

---

## Calling a Function

Creating a function does not automatically start it. The function only starts when the code tells it to. The code does so by using its name (including the brackets).

Example:

```python
def showFruit():
    print("Apple")

showFruit()
```

The computer displays:

```
Apple
```

The last line (`showFruit()`) tells the computer to start the code within the function. Note that it is not indented and therefore no longer part of the function itself — just like the `print` statement in your last exercise.

> **Tip:** You can call a function as many times as you like. Each call runs the function once.

---

## Important Notes

- Functions help organize code.
- Functions can be reused later.
- Indentations tell the computer what belongs to a function.
- Functions only start after being called outside the function.

---

## To Do

Write a program that greets you by extending the code on the right.

```python
# This is the start of the function. It is already in place, but feel free to change the name!
def welcome_message():
    # Here, make the function display a custom greeting
    _____________________

# Call the function, so the greeting is displayed
__________________
```

The console should show:

```
Welcome to Activity Tracker
```

(Calling the function more than once will print the message more than once — both are accepted.)

---

## Your Program Can Now…

Organize code into reusable parts and greet you!
