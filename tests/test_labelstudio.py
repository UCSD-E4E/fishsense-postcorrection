import numpy as np
from e4e.labelstudio import Point, Rectangle

def test_rectangle_contains():
    rect = Rectangle(0, 0, 1, 1, 0)
    point1 = Point(1, 1)
    assert(point1 not in rect)

    rect = Rectangle(0, 0, 1, 1, 45)
    point1 = Point(0, 0.707)
    assert(point1 in rect)

    rect = Rectangle(0, 0, 4, 2, 45)
    point1 = Point(1, 1)
    assert(point1 in rect)

    rect = Rectangle(2, 2, 4, 2, 45)
    point1 = Point(3, 3)
    assert(point1 in rect)