# Item Characteristic Curve

Write a function that returns the item characteristic curve for a given three-parameter item response theory model.

Your input is
- `a`: the discrimination parameter of the model
- `b`: the difficulty parameter of the model
- `c`: the base rate parameter of the model
- `theta`: an array of theta values for which the item characteristic curve should be computed

Your output should be:
- `p`: an array with `len(theta)` entries where `p[i]` is the value of the item characteristic curve at `theta[i]`
