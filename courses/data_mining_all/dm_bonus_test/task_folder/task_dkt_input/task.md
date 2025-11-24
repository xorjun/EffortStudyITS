# Deep Knowledge Tracing Input Conversion

Write a python function `dkt_input` that converts a sequence of student task attempts into a valid input for a deep knowledge tracing model.

As input, your function should accept a single numpy array `X` of shape `(T, 2)` which represents the data of a single student who attempted `T` tasks. The first column are the task indices (from 0 to n-1, where n is the number of tasks), and the second column are 0 or 1, depending on whether the student was successful or not.

The output of your function should be a numpy array `Xhat` of shape `(T, 2*n)`. Row t should represent the attempt of the student at time t-1. Column j should be 1 if the student successfully solved task j, and column n+j should be 1 if the student failed at task j. Every other entry in the row should be zero.
