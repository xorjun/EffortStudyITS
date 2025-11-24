#!function!#
def training_loop(X, Y, model, loss_fun, optim, num_epochs):
#!prefix!#
    """ Implements a deep learning training loop of the pytorch variety. """

    for t in range(num_epochs):
        # zero out any past gradient information
        optim.zero_grad()
        # compute the predictions
        Ypred = model(X)
        # compute the loss
        loss  = loss_fun(Ypred, Y)
        # compute backprop
        loss.backward()
        # adapt parameters
        optim.step()

    return model
