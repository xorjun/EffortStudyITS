# Task 5 — Store Multiple Study Sessions

## Learning Content

Programs sometimes need to store many pieces of information together. For example, an Activity Tracker may store:

- Exercises
- Hobbies

Programmers use **lists** to store multiple items together.

---

## Creating a List

An empty list looks like this:

```python
[]
```

Example:

```python
fruits = []
```

Variables can also store lists. Here, we store an empty list into a variable called `fruits`. Now the program has an empty list.

---

## Adding Items to a List

For adding items to a list, we use:

```python
.append()
```

The program needs to know two things to add an item to a list:

1. Which list
2. Which item

We tell the program which item by adding it within `()`, the way we did before. We tell the program which list by adding `.append` after the name of the list, separated by a dot.

---

## Example

```python
fruits = []
fruits.append("Apple")
fruits.append("Orange")
```

The list now contains:

```
['Apple', 'Orange']
```

---

## Printing a List

Sometimes we want to display all items stored in a list.

```python
fruits = []
fruits.append("Apple")
fruits.append("Orange")
print(fruits)
```

Computer displays:

```
['Apple', 'Orange']
```

---

## Important Notes

- Lists store multiple items together.
- `[]` creates a list.
- `.append()` adds new items to a variable containing a list.
- `.append()` needs to follow the list we wish to append items to, separated by a dot.
- Items are added one by one.

---

## To Do

Create a list of study sessions and return it.

```python
def start_sessions():
    # Create an empty list called sessions
    sessions = _____

    # Add the first session to the list
    sessions.________("Python")

    # Add the second session to the list
    sessions.________("Mathematics")

    # Return the list
    return sessions
```

The function should return:

```
['Python', 'Mathematics']
```

---

## Your Program Can Now…

Store multiple activities.
