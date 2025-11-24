# Deep Learning Training Loop

Write a python function `training_loop` that implements the basic deep learning training loop in pytorch.

Your function receives the following inputs:
- X: A tensor of training data
- Y: A tensor of expected predictions for this training data
- model: A deep neural network that outputs predictions when applied to X
- loss_fun: A function that takes predictions and expected predictions as input and returns a loss value
- optim: a pytorch optimizer (you may assume that this has already been initialized with a learning rate and other hyper-parameters)
- num_epochs: a desired number of training epochs

Your function should apply `num_epochs` steps of training. In each step, you should zero out past gradients, compute the predictions of the model, compute the loss, perform backpropagation, and ask the optimizer to adapt the parameters.

Then, your function should returned the trained `model`.
