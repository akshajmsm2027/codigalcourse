class ExpressionSolver:
    def __init__(self, expression):
        """
        Constructor to initialize the mathematical expression.
        """
        self.expression = expression

    def validate_expression(self):
        """
        Validates the expression to ensure it only contains valid characters.
        """
        allowed_chars = "0123456789+-*/(). "
        for char in self.expression:
            if char not in allowed_chars:
                raise ValueError(f"Invalid character '{char}' in expression.")
        return True

    def solve(self):
        """
        Solves the mathematical expression using Python's eval().
        """
        try:
            self.validate_expression()
            result = eval(self.expression)
            return result
        except Exception as e:
            return f"Error: {e}"

class ExpressionPrinter:
    @staticmethod
    def print_result(expression, result):
        """
        Prints the expression and its result in a formatted way.
        """
        print(f"Expression: {expression}")
        print(f"Result: {result}")

if __name__ == "__main__":
    print("Welcome to the Expression Solver!")
    user_expression = input("Enter a mathematical expression to solve: ")

    
    solver = ExpressionSolver(user_expression)
    result = solver.solve()

    
    ExpressionPrinter.print_result(user_expression, result)
