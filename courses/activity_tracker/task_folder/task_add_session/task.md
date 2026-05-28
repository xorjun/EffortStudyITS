# Add One Study Session

Sometimes one piece of information is not enough.

A study session may need to store:

- the subject
- the study duration

In Python, a list can store multiple values together.

A list can even contain **another list** inside it.

## Storing Multiple Values Together

```python
session = ["Mathematics", 45]
```

This list stores:

- `"Mathematics"` → the subject
- `45` → the duration

## Lists Inside Lists

A larger list can contain many study sessions.

```python
sessions = []

sessions.append(["Mathematics", 45])
sessions.append(["Physics", 30])
```

Now the list becomes:

```
[["Mathematics", 45], ["Physics", 30]]
```

Each inner list represents one study session.

## Converting Text to a Number

Sometimes numbers are stored as text.

Example:

```
"45"
```

This is text, not a real number.

To convert text into a number, we use `int()`.

```python
duration = int("45")
```

Now `duration` becomes the number:

```
45
```

## Example

```python
def add_movie(movies, name, year_text):
    year = int(year_text)
    movies.append([name, year])
    return movies
```

Calling the function:

```python
add_movie([], "Inception", "2010")
```

returns:

```
[["Inception", 2010]]
```

## To Do

Write a function named `add_session` that receives `sessions`, `subject`, and `duration_text`.

Convert `duration_text` to an integer, append a list `[subject, duration]` to the existing `sessions` list, and return `sessions`.

For example, `add_session([], "Mathematics", "45")` should return `[["Mathematics", 45]]`.