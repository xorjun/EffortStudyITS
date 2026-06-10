# Task 3 — Store Information

## Learning Content

Programs often need to remember information. For example, an Activity Tracker may need to remember:

- the activities
- the activity duration

Programs store information using **variables**. A variable is simply a name that stores information.

---

## Creating a Variable

Example:

```python
fruit = "Mango"
```

Here:

- `fruit` is the variable name
- `=` stores the information
- `"Mango"` is the stored text

Now the program remembers the word:

```
Mango
```

---

## Using Stored Information

Once information is stored in a variable, we can use it later.

Example:

```python
fruit = "Apple"
print(fruit)
```

Computer displays:

```
Apple
```

The program displays the stored value. Now it is no longer within `""`, because the `""` is part of the stored information.

---

## Reusing Information

Programs can store information using variables.

Earlier, we used:

```python
fruit = "Apple"
```

This stores the text `"Apple"` inside the variable name. Functions can also store information in a similar way.

When we call a function, the information inside the brackets is temporarily stored so the function can use it. The name of the variable is set during the definition of the program; the value — what it contains — is set when the function is called. This allows the same function to work with different information.

---

## Example

```python
def showFruit(fruit):
    print(fruit)

showFruit("Orange")
```

Computer displays:

```
Orange
```

---

## Understanding the Example

Here:

- The function temporarily stores that text inside the variable `fruit`.
- `showFruit("Orange")` passes the text `"Orange"` into the function. The computer understands this to mean `fruit = "Orange"` when `showFruit` starts.
- Inside the function: `print(fruit)` — the program replaces `fruit` with `Orange`, then prints it.

---

## Important Notes

- Variables store information.
- `=` stores information inside a variable.
- Calling a function can also temporarily store information.
- Functions can reuse the same code with different information.

---

## To Do

Complete the missing parts.

```python
# This is the start of the function. It is already in place, but feel free to change the name!
def remember_subject(subject):
    # Store the subject that was passed into the function
    study_subject = _____

    # Display the stored subject
    print(study_subject)

# Use the function above to display a few subjects, one by one
remember_subject(_____)
remember_subject(_____)
```

The program should print each subject you pass in, on its own line.

---

## Your Program Can Now…

Reuse the same code with different information.
