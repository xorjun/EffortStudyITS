from example_solution import training_loop
#!cut_imports!#

class Model:
    
    def __init__(self):
        pass

    def forward(self, X):
        return None

    def __call__(self, X):
        return self.forward(X)

class OptimizerAndLoss:
    
    def __init__(self):
        self.epoch_count = 0
        self.has_grad_info = None

    def zero_grad(self):
        self.has_grad_info = False

    def backward(self):
        if self.has_grad_info is True or self.has_grad_info is None:
            raise ValueError('The \'backward\' function was called without calling zero_grad on the optimizer, first.')
        self.has_grad_info = True

    def step(self):
        if self.has_grad_info is False or self.has_grad_info is None:
            raise ValueError('The \'step\' functin was called without calling backward on the loss, first.')
        self.epoch_count += 1        


class LossFun:

    def __init__(self, optim):
        self.optim = optim

    def __call__(self, Ypred, Y):
        return self.optim

def test_training_loop():
    X = None
    Y = None
    model = Model()
    optim = OptimizerAndLoss()
    loss_fun = LossFun(optim)

    res = training_loop(X, Y, model, loss_fun, optim, 0)

    assert (res is model), f"The training_loop function should return the trained model in the end, not {str(res)}"

    assert (optim.epoch_count == 0), f"If num_epochs is set to zero, the training_loop function should not perform any calls to the 'step' function of the optimizer."

    res = training_loop(X, Y, model, loss_fun, optim, 1000)

    assert (res is model), f"The training_loop function should return the trained model in the end, not {str(res)}"

    assert (optim.epoch_count == 1000), f"If num_epochs is set to 1000, the training_loop function should call the 'step' function of the optimizer exactly 1000 times, not {optim.epoch_count} times."
    
