#!plot_function!#
import matplotlib.pyplot as plt
from math import exp

def compare_lines():
#!prefix!#
    xs = [x * 0.1 for x in range(21)]
    ys = [x for x in xs]
    plt.plot(xs, ys)
    ys = [x**2 for x in xs]
    plt.plot(xs, ys)
    ys = [exp(x) for x in xs]
    plt.plot(xs, ys)
    plt.legend(['linear', 'square', 'exp'])
    plt.show()
