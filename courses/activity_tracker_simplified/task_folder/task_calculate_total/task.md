# Task 6 — Repeat Actions and Calculate Total Study Time

This task combines two ideas from the document:

1. **Repeat Actions for Multiple Activities** (docx Task 6) — using a loop.
2. **Calculate Total Study Time** (our test) — summing the loop's values.

## Learning Content: Repeat Actions for Multiple Activities

Programs can repeat actions to deal with multiple items in a list.

Example:

```python
numbers = [10, 20, 30]
for number in numbers:
    print(number)
```

Console output:

```
10
20
30
```

The loop processes one item at a time.

### Understanding the Loop

In this example:

```python
for number in numbers:
```

- takes one item from the list
- temporarily stores it in the variable `number`
- starts the indented code
- repeats the same steps for the next item
- stops when there are no more items left in the list

The indentation is important here as well. Inside a loop, indentation tells the program which lines belong to the repeated part.

---

## Learning Content: Calculate the Total

A variable can keep track of the total while the loop runs.

```python
times = [10, 20, 30]

total = 0

for time in times:
    total = total + time

print(total)
```

Console output:

```
60
```

### Step-by-Step Explanation

The program:

1. starts with `total = 0`
2. adds 10 → total is 10
3. adds 20 → total is 30
4. adds 30 → total is 60
5. returns the final total

---

## Important Notes

- Loops repeat actions.
- Loops process items one by one.
- Totals often start at `0`.
- The total changes during each loop step.

---

## To Do

Complete the missing part.

```python
def total_activity_time(times):
    total = 0

    for time in times:
        total = total + ______

    return total
```

Example input: `[20, 30, 10]`
Expected return value: `60`

---

## Your Program Can Now…

Display multiple activities one by one from a list, and sum their durations.
