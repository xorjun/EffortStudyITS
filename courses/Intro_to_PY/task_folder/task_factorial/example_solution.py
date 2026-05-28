#!function!#
def factorial(n: int):
#!prefix!#
    if type(n) is not int:
        raise ValueError("The factorial function is only defined for integer inputs.")
    if n < 0:
        raise ValueError("Factorial is undefined for negative numbers.")
    elif n == 0:
        return 1
    else:
        result = 1
        for i in range(1, n + 1):
            result *= i
        return result

