#!plot_function!#
import matplotlib.pyplot as plt
import numpy as np

def scatter():
#!prefix!#
    xs = np.random.randn(100)
    ys = np.random.randn(100)

    plt.plot(xs, ys, 'o')
    plt.show()
