#!function!#
import numpy as np
from sklearn.linear_model import LogisticRegression

def irt_two(abilities, x): 
#!prefix!#
    model = LogisticRegression(penalty = 'l2', C = 1.0, fit_intercept = True)
    model.fit(np.expand_dims(abilities, 1), x)
    a = model.coef_[0, 0]
    if abs(a) < 1E-3:
        b = 0.
    else:
        b = -model.intercept_[0] / a
    
    return a, b