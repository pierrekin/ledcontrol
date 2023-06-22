def scale(x, input_min, input_max, output_min=0, output_max=1):
    a = output_min
    b = (x - input_min) / (input_max - input_min)
    c = output_max - output_min

    return a + b * c


def clamp(x, lower=0, upper=1):
    return min(max(x, lower), upper)
