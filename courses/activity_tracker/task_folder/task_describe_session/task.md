# Describe One Session with Indices

Lists store items in order.

Each item in a list has a position called an **index**.

In Python:

- the first item has index `0`
- the second item has index `1`
- the third item has index `2`

Indexing allows us to access specific values from a list.

## Accessing Items with Indices

```python
colors = ["Red", "Blue", "Green"]

print(colors[0])
print(colors[1])
```

This outputs:

```
Red
Blue
```

## Using Indices with Study Sessions

A study session list contains:

- the subject
- the duration

```python
session = ["Mathematics", 45]
```

Here:

- `session[0]` → `"Mathematics"`
- `session[1]` → `45`

## Combining Text and Values

We can combine text and values to create readable messages.

```python
name = "Alice"
age = 20

message = "Name: " + name + ", Age: " + str(age)

print(message)
```

This outputs:

```
Name: Alice, Age: 20
```

## Converting Numbers to Text

A number cannot be directly combined with text.

We use `str()` to convert a number into text.

```python
duration = 45

text_duration = str(duration)
```

Now the number can be combined inside a string.

## Example

```python
def describe_book(book):
    return "book[0] = " + book[0] + ", book[1] = " + str(book[1])
```

Calling:

```python
describe_book(["Python Basics", 120])
```

returns:

```
book[0] = Python Basics, book[1] = 120
```

## To Do

Write a function named `describe_session` that receives one session list named `session`.

Use list indexing to create and return a string in exactly this format:

`session[0] = <subject>, session[1] = <duration>`

For example, `describe_session(["Mathematics", 45])` should return `"session[0] = Mathematics, session[1] = 45"`.