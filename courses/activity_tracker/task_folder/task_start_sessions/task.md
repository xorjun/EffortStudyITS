# Start a Session List

Programs often need to store multiple pieces of information together.

In Python, we can use a **list** to keep many items in one place.

A list can store:

- study subjects
- session times
- names
- messages

Lists keep items in order, and new items can be added later.

## Creating an Empty List

An empty list is created using square brackets:

```python
activities = []
```

Right now, the list has no items inside it.

## Adding Items to a List

We can add new items using `append()`.

```python
activities = []
activities.append("Reading")
```

Now the list contains:

```
["Reading"]
```

## Lists Can Store Multiple Items

```python
activities = []
activities.append("Reading")
activities.append("Exercise")
activities.append("Music")
```

This creates:

```
["Reading", "Exercise", "Music"]
```

## Using Lists Inside Functions

A function can create a list and return it.

```python
def create_activities():
    activities = []
    return activities
```

When the function runs, it returns an empty list.

## To Do

Write a function named `start_sessions` that does not receive any parameters.

Create an empty list named `sessions` and return it.

For example, `start_sessions()` should return `[]`.