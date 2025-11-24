#!plot_function!#
import matplotlib.pyplot as plt

def plot_square():
#!prefix!#
    xs = list(range(1, 11))
    ys = [(x**2+3) for x in xs]
    plt.plot(xs, ys)
    plt.show()
