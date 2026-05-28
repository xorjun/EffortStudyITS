# Give a Simple Recommendation

Programs can make decisions based on conditions.

For example, a study tracker can:

- encourage the user to study more
- congratulate the user for studying enough

In Python, we use `if` and `else` for this.

## Using `if`

An `if` statement checks whether something is true.

```python
age = 15

if age < 18:
    print("Minor")
```

This prints:

```
Minor
```

because `15` is less than `18`.

## Using `else`

`else` is used when the condition is **not** true.

```python
score = 80

if score < 50:
    print("Try again")
else:
    print("Well done")
```

This outputs:

```
Well done
```

## Returning Messages from Functions

A function can return different messages depending on a condition.

```python
def weather_message(temperature):
    if temperature < 20:
        return "Cold day"
    else:
        return "Warm day"
```

Calling:

```python
weather_message(25)
```

returns:

```
Warm day
```

## To Do

Write a function named `study_recommendation` that receives `total_minutes`.

If `total_minutes` is less than `60`, return exactly `"Study a little longer today."`

Otherwise, return exactly `"Great job! You reached at least 60 minutes."`

This recommendation is meant to be the final step after you calculate the total study time for all sessions.