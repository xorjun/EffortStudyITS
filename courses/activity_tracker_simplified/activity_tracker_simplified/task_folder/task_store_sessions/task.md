# Store Multiple Study Sessions

Programs sometimes need to store many pieces of information together.

For example, an Activity Tracker may store:

- Python
- Mathematics
- Physics

Python uses **lists** to store multiple items together.

---

## Creating a List

An empty list looks like this:

```python
sessions = []
```

---

## Adding Items to a List

Python uses `append()` to add new items.

```python
sessions = []

sessions.append("Python")
sessions.append("Mathematics")
```

The list now contains:

```
['Python', 'Mathematics']
```

---

## Printing a List

```python
sessions = []

sessions.append("Python")
sessions.append("Mathematics")

print(sessions)
```

Console output:

```
['Python', 'Mathematics']
```

---

## Important Notes

- lists store multiple items together
- `[]` creates an empty list
- `append()` adds new items
- items are added one after another

---

## To Do

Complete the function so it creates a list, adds both subjects to it, and returns the list.

Expected return value:

```
['Python', 'Mathematics']
```
