

def fibonacci_series(n):
    """Function to generate Fibonacci series up to n terms."""
    if n <= 0:
        print("Please enter a positive integer.")
        return
    elif n == 1:
        print("Fibonacci series up to 1 term: [0]")
        return
    else:
        fib_sequence = [0, 1]  
        for i in range(2, n):
            next_term = fib_sequence[-1] + fib_sequence[-2]
            fib_sequence.append(next_term)
        print(f"Fibonacci series up to {n} terms: {fib_sequence}")

if __name__ == "__main__":
    try:
        
        n = int(input("Enter the number of terms for the Fibonacci series: "))
        fibonacci_series(n)
    except ValueError:
        print("Invalid input! Please enter an integer.")
