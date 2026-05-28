from example_solution import pfa_extended
#!cut_imports!#
import numpy as np

def test_pfa_extended():
    # test a simple case with only one task and one skill
    X = np.array([[0, 0, 0, 0, 0], [0, 0, 1, 1, 1]]).T
    Q = np.array([[1]])

    gamma, rho, beta, b = pfa_extended(X, Q)
    
    # check the format of the data
    assert len(gamma) == 1, "For a Q matrix with only one skill, gamma should have only one entry"
    assert len(rho) == 1, "For a Q matrix with only one skill, gamrhoma should have only one entry"
    assert len(beta) == 1, "For a Q matrix with only one skill, beta should have only one entry"
    assert len(b) == 1, "For a Q matrix with only one task, b should have only one entry"

    assert gamma[0] > 0, "For our example case, gamma should be positive. Check whether you have formatted the input data correctly."
    assert rho[0] > 0, "For our example case, rho should be positive. Check whether you have formatted the input data correctly."
    assert beta[0] < 0, "For our example case, beta should be negative. Check whether you have formatted the input data correctly."
    assert b[0] > 0, "For our example case, b should be positive. Check whether you have formatted the input data correctly."

    # check that the prediction would be correct
    theta = rho[0] + beta[0]
    assert theta < b[0], f"We tested a data set with only one task, one skill, and successes {X[:, 0]}. For this data set, we expected that beta[0] + rho[0] should still be below the difficulty of the task so that the model correctly predicts failure for the second attempt, but it wasn't."
    theta += rho[0]
    assert theta > b[0], f"We tested a data set with only one task, one skill, and successes {X[:, 0]}. For this data set, we expected that beta[0] + 2*rho[0] should still be above the difficulty of the task so that th emodel correctly predicts success for the third attempt, but it wasn't."

    # test a more complicated example with multiple tasks and skills
    X = np.array([[0, 1, 0, 1, 0, 2], [0, 0, 0, 1, 1, 0]]).T
    Q = np.array([[1, 0], [0, 1], [1, 1]])

    gamma, rho, beta, b = pfa_extended(X, Q)

    # check the format of the data
    assert len(gamma) == 2, "For a Q matrix with two skills, gamma should have length 2"
    assert len(rho) == 2, "For a Q matrix with two skills, rho should have length 2"
    assert len(beta) == 2, "For a Q matrix with two skills, beta should have length 2"
    assert len(b) == 3, "For a Q matrix with three tasks, b should have length 3"

    #assert np.all(gamma > 0), "For our example case, gamma should be positive. Check whether you have formatted the input data correctly."
    assert np.all(rho > 0), "For our example case, rho should be positive. Check whether you have formatted the input data correctly."
    assert np.all(beta < 0), "For our example case, beta should be negative. Check whether you have formatted the input data correctly."
    #assert np.all(b > 0), "For our example case, b should be positive. Check whether you have formatted the input data correctly."

    # check that the prediction would be correct
    theta = rho[0] + beta[0]
    assert theta < b[0], f"We tested a data set where a student fails a task for a skill with one past failure, so beta + rho should be smaller than the difficulty of the task - but it wasn't."
    theta = 2*rho[0] + beta[0]
    assert theta > b[0], f"We tested a data set where a student succeeds at a task for a skill with two past failures, so beta + 2*rho should be larger than the difficulty of the task - but it wasn't."
   
    theta = beta[1]
    assert theta < b[1], f"We tested a data set where a student fails the initial attempt for a skill, so beta should be smaller than the difficulty of the task - but it wasn't."
    theta = rho[1] + beta[1]
    assert theta > b[1], f"We tested a data set where a student succeeds at a task for a skill with one past failure, so beta + rho should be larger than the difficulty of the task - but it wasn't."

    theta = 2*rho[0] + gamma[0] + beta[0] + gamma[1] + rho[1] + beta[1]
    assert theta < b[2], f"We tested a data set where a task with two skills is still too hard after two failures and one success in the first skill and one failure and one success in the second skill. But the model predicted success."