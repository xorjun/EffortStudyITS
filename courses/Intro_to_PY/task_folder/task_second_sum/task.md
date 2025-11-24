# Loops

In Python, as in other iterative programming languages, loops are used to repeat parts of a program.

## While Loops

A `while` loop is repeated while a condition holds. For example:

```python
# while loop
i = 0
while i < 5:
    print(i)
    i += 1

cond = True
while cond is True:
    print("Bla")
    cond = False
```

will yield the output:

```
0
1
2
3
4
Bla
```

## For loops

By contrast, a `for` loop is applied for each element in a given list. The elements are automatically put into a variable that can be used inside the loop. For example:

```python
# for loop
for i in range(1,5):
    print(i)
    
for _ in range(5):
    print("Hi")
```

will yield the output:

```
1
2
3
4
Hi
Hi
Hi
Hi
Hi
```

A typical application of loops is to process lists. For example:

```python

my_list = [1, 2, 3, 4, 5]

for i in range(len(my_list)):
    print(my_list[i])
```

will yield the output:

```
1
2
3
4
5
```

As another example:

```python

my_list = [1, 2, 3, 4, 5]

for i in my_list:
    print(i)
```

will yield the same output:

```
1
2
3
4
5
```

## To Do

Define a function

```python
def second_sum(input):
    ...
```
which takes a list of numbers as input and outputs the sum of every second number in the input list, starting from the second number.

For an example, for an input [1, 2, 3, 4, 5], the expected output should be (2 + 4) = 6.

**Hint:** There are two basic approaches to this task: You can slice the input list cleverly, or you can construct a loop that iterates over each second index in the list.