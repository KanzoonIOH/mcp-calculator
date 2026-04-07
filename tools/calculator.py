def add(a: float, b: float) -> float:
    """Add two numbers and return the result."""
    return a + b


def substract(a: float, b: float) -> float:
    """Substract two numbers and return the result."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers and return the result."""
    return a * b


def devide(a: float, b: float) -> float:
    """Divide two numbers and return the result."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b
