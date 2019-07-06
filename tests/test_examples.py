import rita


def test_color_car():
    result = rita.compile('examples/color-car.rita')
    print(result)
