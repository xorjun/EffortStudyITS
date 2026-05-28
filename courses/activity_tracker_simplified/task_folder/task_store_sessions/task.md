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

Complete the missing parts.

```python
def start_sessions():
    sessions = _____

    sessions.________("Python")
    sessions.________("Mathematics")

    return sessions
```

The function should return:

```
['Python', 'Mathematics']
```
