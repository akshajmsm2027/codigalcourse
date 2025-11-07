import math


class Polygon:
    def __init__(self, name):
        self.name = name

    def area(self):
        raise NotImplementedError("This method should be overridden by subclasses")

    def __str__(self):
        return f"This is a {self.name}."

class Rectangle(Polygon):
    def __init__(self, width, height):
        super().__init__("Rectangle")
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)
        self.name = "Square"


class Triangle(Polygon):
    def __init__(self, base, height):
        super().__init__("Triangle")
        self.base = base
        self.height = height

    def area(self):
        return 0.5 * self.base * self.height

class Circle(Polygon):
    def __init__(self, radius):
        super().__init__("Circle")
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2

def main():
    shapes = [
        Rectangle(10, 5),
        Square(4),
        Triangle(6, 3),
        Circle(7)
    ]

    for shape in shapes:
        print(f"{shape}: Area = {shape.area():.2f}")

if __name__ == "__main__":
    main()
