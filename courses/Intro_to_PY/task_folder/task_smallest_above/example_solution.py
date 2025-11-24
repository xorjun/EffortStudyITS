#!function!#
def smallest_above(numbers, threshold):
#!prefix!#
    result = None

    for num in numbers:
        if num > threshold:
            if result is None or num < result:
                result = num

    return result