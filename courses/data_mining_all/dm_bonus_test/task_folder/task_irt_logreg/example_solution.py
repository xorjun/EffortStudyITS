#!function!#
import numpy as np
from sklearn.linear_model import LogisticRegression
def IRT_logreg(data): 
#!prefix!#
    N, m = data.shape
    Xlogreg = np.zeros((N*m, N+m))
    ylogreg = np.zeros(N*m)
    for i in range(N):
        for j in range(m):
            Xlogreg[i*m+j, i] = 1
            Xlogreg[i*m+j, N+j] = 1
            ylogreg[i*m+j] = data[i, j]
    model = LogisticRegression(penalty = 'l2', C = 1.0, fit_intercept = False)
    model.fit(Xlogreg, ylogreg)
    difficulties = -model.coef_[0, -m:]

    return  difficulties