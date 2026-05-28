# Calculate Total Study Time

Programs can repeat actions.

Python uses **loops** to repeat code.

A loop can go through items one by one.

---

## Example

```python
times = [10, 20, 30]

for time in times:
    print(time)
```

Console output:

```
10
20
30
```

The loop prints one number at a time.

---

## Understanding the Loop

In this example:

```python
for time in times:
```

Python:

- takes one item from the list
- stores it in `time`
- runs the indented code
- repeats for the next item

---

## Adding Numbers Together

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

---

## Step-by-Step Explanation

The program:

1. starts with `total = 0`
2. adds 10 → total is 10
3. adds 20 → total is 30
4. adds 30 → total is 60
5. returns the final total

---

## Important Notes

- loops repeat actions
- loops process items one by one
- totals often start at `0`
- the total changes during each loop step

---

## To Do

Complete the function so it adds up all the numbers in the `times` list and returns the total.

Example input: `[20, 30, 10]`

Expected return value: `60`
