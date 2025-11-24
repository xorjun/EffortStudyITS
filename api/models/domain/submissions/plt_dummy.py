class dummy_plt():
    def __init__(self):
        self.func_queue = []
    
    ### Adding Data to the plot

    def plot(self, *args, **kwargs):
        self.func_queue.append({'func': "plot", 'args': args, 'kwargs': kwargs})

    def errorbar(self, *args, **kwargs):
        self.func_queue.append({'func': "errorbar", 'args': args, 'kwargs': kwargs})
        
    def scatter(self, *args, **kwargs):
        self.func_queue.append({'func': "scatter", 'args': args, 'kwargs': kwargs})
        
    def fill_between(self, *args, **kwargs):
        self.func_queue.append({'func': "fill_between", 'args': args, 'kwargs': kwargs})
        
    def bar(self, *args, **kwargs):
        self.func_queue.append({'func': "bar", 'args': args, 'kwargs': kwargs})

    def stackplot(self, *args, **kwargs):
        self.func_queue.append({'func': "stackplot", 'args': args, 'kwargs': kwargs})
        
    def boxplot(self, *args, **kwargs):
        self.func_queue.append({'func': "boxplot", 'args': args, 'kwargs': kwargs})

    def hist(self, *args, **kwargs):
        self.func_queue.append({'func': "hist", 'args': args, 'kwargs': kwargs})
    
    ### Axis configuration

    def xlabel(self, *args, **kwargs):
        self.func_queue.append({'func': "xlabel", 'args': args, 'kwargs': kwargs})

    def xlim(self, *args, **kwargs):
        self.func_queue.append({'func': "xlim", 'args': args, 'kwargs': kwargs})

    def xscale(self, *args, **kwargs):
        self.func_queue.append({'func': "xscale", 'args': args, 'kwargs': kwargs})

    def xticks(self, *args, **kwargs):
        self.func_queue.append({'func': "xticks", 'args': args, 'kwargs': kwargs})

    def ylabel(self, *args, **kwargs):
        self.func_queue.append({'func': "ylabel", 'args': args, 'kwargs': kwargs})

    def ylim(self, *args, **kwargs):
        self.func_queue.append({'func': "ylim", 'args': args, 'kwargs': kwargs})

    def yscale(self, *args, **kwargs):
        self.func_queue.append({'func': "yscale", 'args': args, 'kwargs': kwargs})

    def yticks(self, *args, **kwargs):
        self.func_queue.append({'func': "yticks", 'args': args, 'kwargs': kwargs})

    def suptitle(self, *args, **kwargs):
        self.func_queue.append({'func': "suptitle", 'args': args, 'kwargs': kwargs})

    def title(self, *args, **kwargs):
        self.func_queue.append({'func': "title", 'args': args, 'kwargs': kwargs})

    ### Output

    def legend(self, *args, **kwargs):
        self.func_queue.append({'func': "legend", 'args': args, 'kwargs': kwargs})

    def show(self, *args, **kwargs):
        self.func_queue.append({'func': "show", 'args': args, 'kwargs': kwargs})

plt = dummy_plt()