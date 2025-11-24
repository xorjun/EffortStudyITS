from matplotlib.figure import Figure

class Eval_Figure(Figure):
    """
    This Figure subclass makes sure that all created Axis inside of it are of the correct subclass, Eval_Axis,
    which is able to send the plotted data to evaluation before plotting it.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # This is the critical method to be overloaded to make sure the correct Axes class gets created
    # All calls for new Axis creation route through this one
    def add_subplot(self, *args, **kwargs):
        # make sure the returned Axes are of the right projection
        if kwargs: kwargs['projection'] = "eval_axes"
        else: kwargs = {'projection': "eval_axes"}
        return super().add_subplot(*args, **kwargs)
    
    # Methods the students are not supposed to have access to are overloaded here
    
    def savefig(self, *args, **kwargs):
        raise PermissionError("Method not allowed.")
        # return super().savefig(*args, **kwargs)
