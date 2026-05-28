# Store Information

Programs often need to remember information.

For example, an Activity Tracker may need to remember:

- the activity subject
- the activity duration

Python stores information using **variables**.

A variable is simply a name that stores information.

---

## Creating a Variable

```python
subject = "Python"
```

Here:

- `subject` is the variable name
- `=` stores the information
- `"Python"` is the stored text

Now the program remembers the word: `Python`

---

## Using Stored Information

Once information is stored in a variable, we can use it later.

```python
subject = "Mathematics"

print(subject)
```

Console output:

```
Mathematics
```

---

## Learning About Parameters

Functions can also receive information.

The information inside the brackets is called a **parameter**.

Parameters allow functions to work with different information.

```python
def show_subject(subject):
    print(subject)

show_subject("Physics")
```

Console output:

```
Physics
```

---

## Important Notes

- variables store information
- parameters allow functions to receive information
- `=` stores information inside a variable
- variables help programs remember information temporarily

---

## To Do

Complete the function body so it stores the `subject` in a variable and prints it.

Expected output when called with `"Python"`:

```
Python
```
