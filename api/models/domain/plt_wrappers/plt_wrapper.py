from eval_axes import Eval_Axes
from eval_figure import Eval_Figure

from matplotlib.projections import register_projection

"""
This wrapper is supposed to extract data plotted by students and process them.
WARNING: Students can still access the plt import in this module,
    so this is not 100% secure, since imports cannot be made private (thanks python).
Methods student are not supposed to have access to are simply ommitted from here.
"""

# TODO process data before forwarding to plt

class PLT_Wrapper():
    def __init__(self):
        import matplotlib.pyplot
        self.__plt = matplotlib.pyplot
        
        self.setup();

    ### Managing Figure and Axes

    def figure(self, **fig_kw):
        fig_kw = self.set_figure_class_arg(fig_kw)
        return self.__plt.figure(**fig_kw)

    def gca(self):
        return self.__plt.gca()

    def gcf(self):
        return self.__plt.gcf()

    def subplots(self, *args, **fig_kw):
        fig_kw = self.set_figure_class_arg(fig_kw)
        return self.__plt.subplots(*args, **fig_kw)

    def subplot(self, *args, **kwargs):
        return self.__plt.subplot(*args, **kwargs)

    ### Adding Data to the plot

    def plot(self, *args, **kwargs):
        return self.__plt.plot(*args, **kwargs)

    def errorbar(self, x, y, yerr=None, xerr=None, *args, **kwargs):
        return self.__plt.errorbar(x, y, yerr, xerr, *args, **kwargs)
        
    def scatter(self, x, y, *args, **kwargs):
        return self.__plt.scatter(x, y, *args, **kwargs)
        
    def fill_between(self, x, y1, y2=0, *args, **kwargs):
        return self.__plt.fill_between(x, y1, y2, *args, **kwargs)
        
    def bar(self, x, height, *args, **kwargs):
        return self.__plt.bar(x, height, *args, **kwargs)

    def stackplot(self, x, *args, **kwargs):
        return self.__plt.stackplot(x, *args, **kwargs)
        
    def boxplot(self, x, *args, **kwargs):
        return self.__plt.boxplot(x, *args, **kwargs)

    def hist(self, x, bins=None, *args, **kwargs):
        return self.__plt.hist(x, bins, *args, **kwargs)

    ### Axis configuration

    def xlabel(self, label, *args, **kwargs):
        return self.__plt.xlabel(label, *args, **kwargs)

    def xlim(self, *args, **kwargs):
        return self.__plt.xlim(*args, *kwargs)

    def xscale(self, value, **kwargs):
        return self.__plt.xscale(value, *kwargs)

    def xticks(self, ticks=None, labels=None, *args, **kwargs):
        return self.__plt.xticks(ticks, labels, *args, *kwargs)

    def ylabel(self, label, *args, **kwargs):
        return self.__plt.ylabel(label, *args, *kwargs)

    def ylim(self, *args, **kwargs):
        return self.__plt.ylim(*args, *kwargs)

    def yscale(self, value, **kwargs):
        return self.__plt.yscale(value, *kwargs)

    def yticks(self, ticks=None, labels=None, *args, **kwargs):
        return self.__plt.yticks(ticks, labels, *args, *kwargs)

    def suptitle(self, t, **kwargs):
        return self.__plt.suptitle(t, **kwargs)

    def title(self, label, *args, **kwargs):
        return self.__plt.title(label, *args, **kwargs)

    ### Output

    def draw(self):
        return self.__plt.draw()

    def show(self, *args, **kwargs):
        return self.__plt.show(*args, **kwargs)

    ### Utility

    def set_figure_class_arg(self, kwargs):
        if kwargs: kwargs['FigureClass'] = Eval_Figure
        else: kwargs = {'FigureClass': Eval_Figure}
        return kwargs

    def setup(self):
        register_projection(Eval_Axes)
        self.__plt.close('all')
        self.figure()