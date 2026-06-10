# Task 4 — Return Information

## Learning Content

So far, the functions displayed messages on the screen using `print()`. Functions can also send information back instead of displaying it. For that we use the word:

```python
return
```

The `return` statement sends information out of the function. Other parts of the program can then use that information.

---

## Example

```python
def showFruit():
    return "Apple"
```

This function sends back:

```
Apple
```

---

## Using Returned Information

Returned information can be stored in a variable.

Example:

```python
def showFruit():
    return "Apple"

result = showFruit()
print(result)
```

Console output:

```
Apple
```

---

## Important Notes

- `return` sends information back from a function.
- Returned information can later be stored in variables.
- Functions can return text or numbers.
- `return` helps different parts of the program share information.
- Quotation marks are needed when returning text:

  ```python
  return "Apple"   # text — needs quotation marks
  ```

  Numbers do not need quotation marks:

  ```python
  return 10        # number — no quotation marks
  ```

---

## To Do

Complete the missing parts.

```python
# This is a small driver function that calls your function and prints
# its result. You do not need to understand everything here.
def very_complicated_function():
    activity = get_activity()
    print(activity + " is very fun!")

# This is the start of the function you need to complete.
def get_activity():
    # In the next line, return the text "Walking" — or any other activity
    _____________________

# This calls the driver function. Once you have added the return,
# starting the program will print "<activity> is very fun!".
very_complicated_function()
```

---

## Your Program Can Now…

Send information from one part of the program to another.
