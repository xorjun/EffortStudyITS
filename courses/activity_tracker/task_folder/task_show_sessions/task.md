# Show All Study Sessions

Programs often need to repeat the same action multiple times.

For example, a study tracker may need to:

- show every study session
- display every subject
- process all stored data

In Python, we use a **for loop** to go through items one by one.

## Using a `for` Loop

A `for` loop takes one item from a list at a time.

```python
colors = ["Red", "Blue", "Green"]

for color in colors:
    print(color)
```

This will output:

```
Red
Blue
Green
```

## Looping Through Study Sessions

A study session list can look like this:

```python
sessions = [
    ["Mathematics", 45],
    ["Physics", 30]
]
```

Each item contains:

- a subject
- a duration

## Accessing Values Inside Each Session

Inside the loop:

- `session[0]` gives the subject
- `session[1]` gives the duration

```python
session = ["Mathematics", 45]

print(session[0])
print(session[1])
```

This outputs:

```
Mathematics
45
```

## Printing Formatted Messages

We can combine text and values inside `print()`.

```python
subject = "Physics"
duration = 30

print("Subject:", subject, "- Duration:", duration)
```

This outputs:

```
Subject: Physics - Duration: 30
```

## Example

```python
def show_fruits(fruits):
    for fruit in fruits:
        print("Fruit:", fruit)
```

Calling:

```python
show_fruits(["Apple", "Banana"])
```

will print:

```
Fruit: Apple
Fruit: Banana
```

## To Do

Write a function named `show_sessions` that receives a list named `sessions`.

Each entry in `sessions` is a list of the form `[subject, duration]`.

Use a `for` loop to print each session on its own line in the format `"Subject: <subject>, Duration: <duration> minutes"`.

For example, for `[["Mathematics", 45], ["Physics", 30]]` the function should print:

```
Subject: Mathematics, Duration: 45 minutes
Subject: Physics, Duration: 30 minutes
```