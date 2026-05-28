# Return Information

Functions can also send information back.

Python uses the word `return`.

The `return` statement sends information out of the function.

Other parts of the program can then use that information.

---

## Example

```python
def get_subject():
    return "Python"
```

This function sends back: `Python`

---

## Using Returned Information

Returned information can be stored in a variable.

```python
def get_number():
    return 10

result = get_number()

print(result)
```

Console output:

```
10
```

---

## Important Notes

- `return` sends information back from a function
- returned information can be stored in variables
- functions can return text or numbers
- `return` helps different parts of the program share information

---

## To Do

Complete the function so it sends back the value `"Mathematics"`.

Expected return value:

```
Mathematics
```
