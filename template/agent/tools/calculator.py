def add(a: int, b: int) -> int:
    """
    Plus 2 numbers

    Args:
        a (int): the first number
        b (int): the second number
    
    Output:
        Result of plus a and b (int)
    """
    return a + b


def subtract(a: int, b: int) -> int:
    """
    Minus 2 numbers

    Args:
        a (int): the first number
        b (int): the second number

    Output:
        Result of minus a and b (int)
    """
    return a - b

def multiply(a: int, b: int) -> int:
    """
    Multiply 2 numbers

    Args:
        a (int): the first number
        b (int): the second number

    Output:
        Result of multiply a and b (int)
    """
    return a * b

def divide(a: int, b: int) -> float:
    """
    Divide 2 numbers

    Args:
        a (int): the first number
        b (int): the second number

    Output:
        Result of divide a and b (float)
    """
    if b == 0:
        return 0.0
    return a / b

def mod(a: int, b: int) -> int:
    """
    Modulus of 2 numbers

    Args:
        a (int): the first number
        b (int): the second number

    Output:
        Result of modulus a and b (int)
    """
    if b == 0:
        return 0
    return a % b

