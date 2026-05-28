#!plot_function!#
import matplotlib.pyplot as plt

pre_test_control = [27, 31, 30, 20, 41, 39, 20, 27, 33, 22, 22, 29, 25, 41, 23, 17, 34, 23, 48, 19, 28, 38, 22, 34, 36, 33, 40, 39]
pre_test_intervention = [24, 38, 34, 37, 31, 37, 25, 23, 12, 31, 36, 34, 41, 14, 7, 30, 42, 25, 29, 17, 40, 29, 33, 24, 38, 26, 41, 37, 41]
post_test_control = [40, 34, 40, 40, 54, 51, 33, 36, 46, 29, 41, 40, 40, 47, 36, 30, 40, 27, 53, 26, 33, 46, 34, 45, 49, 47, 41, 52]
post_test_intervention = [50, 62, 51, 50, 44, 57, 50, 37, 38, 56, 46, 48, 59, 37, 29, 54, 62, 44, 53, 40, 63, 46, 50, 50, 53, 48, 50, 65, 61]

def box_plot():
#!prefix!#
    plt.boxplot(
        [pre_test_control,
        pre_test_intervention,
        post_test_control,
        post_test_intervention],
        tick_labels = ['control pre', 'intervention pre', 'control post', 'intervention post']
    )
    plt.xlabel('condition')
    plt.ylabel('test points')
    plt.show()
