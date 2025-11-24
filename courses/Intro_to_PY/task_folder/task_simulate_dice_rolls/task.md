# Random samples

**numpy.random** is a module which can be used to generate random elements. For example:

```python
import numpy as np
dice_rolls = np.random.randint(1, 50) # generate a random integer between 1 and 50
print(dice_rolls)
```
will create an output like:

```
24
```

## Random seeds

If you rerun the code above, the number will most likely not repeat. To receive the same random number every time, you can **seed** your generator:

```python
import numpy as np
np.random.seed(4)
die_rolls = np.random.randint(1, 50)
print(die_rolls)
```

will yield the output:

```
47 
```

Now, repeated executions of the code will always yield the same result.


## To Do

Write a python function that receives a number as input and rolls the according number of fair, six-sided dice. The function should return the average of all dice rolls. Include the random seed as a second argument, so that the behaviour could be replicated, if necessary. 

```python
def simulate_dice_rolls(num_rolls, random_seed=None):
    ...
    return average_value
```