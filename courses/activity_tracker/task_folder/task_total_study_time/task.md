# Calculate Total Study Time

Programs often need to calculate totals.

For example, a study tracker may want to calculate the total number of minutes studied.

To do this, we use an **accumulator variable**.

An accumulator starts with a value and is updated inside a loop.

## Starting a Total

Usually, the total starts at `0`.

```python
total = 0
```

## Adding Values Inside a Loop

```python
total = total + 10
```

This updates the total by adding a new value.

## Example

```python
numbers = [5, 10, 15]

total = 0

for number in numbers:
    total = total + number

print(total)
```

This outputs:

```
30
```

## Using This with Study Sessions

A study session looks like this:

```python
["Mathematics", 45]
```

Here:

- `session[0]` is the subject
- `session[1]` is the duration

We only add the **durations**.

## Another Example

```python
def total_scores(scores):
    total = 0
    for score in scores:
        total = total + score
    return total
```

Calling:

```python
total_scores([20, 15, 5])
```

returns:

```
40
```

## To Do

Write a function named `total_study_time` that receives a list named `sessions`.

Each element of `sessions` is a list `[subject, duration]`.

Use an accumulator variable to sum all durations and return the total number of minutes.

For example, `[["Mathematics", 45], ["Physics", 30]]` should return `75`.