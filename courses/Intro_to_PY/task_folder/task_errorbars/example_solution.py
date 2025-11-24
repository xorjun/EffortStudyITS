#!plot_function!#
import matplotlib.pyplot as plt
import numpy as np

def errorbars():
#!prefix!#
    data1 = [1, 3, 2, 3, 2, 3, 2]
    data2 = [3, 2, 1, 2, 3, 2, 1]

    xs = [1, 2]
    ys = [np.mean(data1), np.mean(data2)]
    yerrs = [np.std(data1), np.std(data2)]

    plt.bar(xs, ys, yerr = yerrs)
    plt.xticks(xs, ['data 1', 'data 2'])
    plt.show()
