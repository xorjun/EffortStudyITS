from example_solution import factorial as factorial
#!cut_imports!#
def test_large_factorial():
    # Test factorial of 20
    assert factorial(20) == 2432902008176640000, "Factorial of 20 is 2.432902e+18"
