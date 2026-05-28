from example_solution import mean_and_var
#!cut_imports!#
def test_mean_and_var():
    x = [1,1,1,1,1,1]
    res = mean_and_var(x)

    #Output format
    assert type(res) == tuple and len(res) == 2, "Output is of the wrong format, it should be a tuple of length 2" 

    #var of a constant
    res = mean_and_var([5])[1]
    assert res == 0, f"The standard deviation of a constant should be 0 but is {res}"

    #Mean and var of constant sequence
    res = mean_and_var(x)
    assert res == (1.0,0.0), f"Mean and variance of a constant sequence (c,...,c) should be (c, 0), but is {res}"

    #Mean and var of simple sequence
    res = mean_and_var([-1, 0, 1])
    assert abs(res[0] - 0.) < 1E3 and abs(res[1] - (2./3.)) < 1E-3, f"Mean and variance of the list [-1, 0, 1] should be 0 and 2/3, but is {res}"

    #Mean and var for long sequence
    x = [0.81576194, 0.51398175, 0.56261593, 0.81676137, 0.23038586,
       0.88764996, 0.88568396, 0.84614778, 0.310661  , 0.05290907,
       0.62032513, 0.05587429, 0.94184768, 0.4829302 , 0.8582894 ,
       0.71162877, 0.33999384, 0.39619025, 0.13423464, 0.84842121,
       0.49465688, 0.06964644, 0.63324833, 0.01573582, 0.8049175 ,
       0.21038944, 0.20113233, 0.51149964, 0.1068265 , 0.53042347,
       0.52618041, 0.09963717, 0.20989386, 0.30059913, 0.29615553,
       0.61216746, 0.62014223, 0.51364637, 0.31911852, 0.91622346,
       0.2369842 , 0.86472512, 0.78025146, 0.91363438, 0.39521617,
       0.52407898, 0.11741483, 0.04448029, 0.88569193, 0.99497197,
       0.76622834, 0.85603396, 0.03676529, 0.26125318, 0.11063025,
       0.36162712, 0.63168195, 0.06838895, 0.02770522, 0.99520249,
       0.40268088, 0.36964884, 0.39126346, 0.62938722, 0.37575843,
       0.87027801, 0.17735245, 0.89138505, 0.73136677, 0.83435799,
       0.77947838, 0.82539821, 0.88780011, 0.55848545, 0.45550078,
       0.6304266 , 0.92011949, 0.86910712, 0.13468223, 0.98908817,
       0.01265963, 0.87443428, 0.97142216, 0.4628126 , 0.24787151,
       0.12766514, 0.94653958, 0.18802227, 0.37621816, 0.41822555,
       0.18712478, 0.21462281, 0.39920795, 0.59288027, 0.0850282 ,
       0.95508564, 0.17085048, 0.58207866, 0.29303236, 0.33187382]
    
    res = mean_and_var(x)
    x_mean = sum(x)/len(x)
    x_sum_squared_diff = sum((x[i] - x_mean) ** 2 for i in range(0,len(x)))
    x_var = (x_sum_squared_diff / len(x))

    assert x_mean == res[0], "Mean of a long array is wrong"
    assert x_var == res[1], "Variance of a long array is wrong"
