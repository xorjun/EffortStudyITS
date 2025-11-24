#!function!#
def second_sum(input_list):
#!prefix!#
    result = 0
    for i in input_list[1::2]:
        result += i
    return result

