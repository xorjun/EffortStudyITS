from example_solution import factorial as factorial
#!cut_imports!#
def test_factorial():
    # Test factorial of another type
    got_exception = False
    try:
        factorial("test string")
    except Exception:
        got_exception = True
    assert got_exception, "factorial of a string should be undefined and throw an error."

    # Test factorial of a negative number
    got_exception = False
    try:
        factorial(-1)
    except Exception:
        got_exception = True
    assert got_exception, "factorial of a negative number should be undefined and throw an error."

    # Test factorial of 0
    assert factorial(0) == 1, "Factorial of 0 is 1"
    
    # Test factorial of positive numbers
    assert factorial(1) == 1, "Factorial of 1 is 1"
    assert factorial(5) == 120, "Factorial of 5 is 120"
    assert factorial(10) == 3628800, "Factorial of 10 is 3628800"