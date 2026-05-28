# Remember a Study Subject

Programs often need to remember information so it can be used later.

In Python, we can store information inside a **variable**.

A variable is a named place where the program keeps something temporarily.

For example, a program can remember:

- a study subject
- a username
- a score
- a message

## Using Variables

A variable is created using the `=` symbol.

```python
study_subject = "Python"
```

This stores the text `"Python"` inside the variable `study_subject`.

## Using a Function Parameter

Functions can receive information from outside.

The value inside the brackets is called a **parameter**.

```python
def show_subject(subject):
    print(subject)
```

Here, the function receives a `subject` and uses it inside the function.

## Returning a Value

A function can give a value back using `return`.

```python
def get_subject():
    subject = "Python"
    return subject
```

The function returns the value stored in `subject`.

## Example

```python
def remember_subject(subject):
    study_subject = subject
    return study_subject
```

If the function is called like this:

```python
remember_subject("Python")
```

the returned value will be:

```
Python
```

## To Do

Write a function named `remember_subject` that receives a subject as the parameter `subject`.

Inside the function, store that value in a variable named `study_subject` and return `study_subject`.

You will use that remembered subject again when you add study sessions later in the course.