def plus(a: int, b: int) -> int:
    """
    Docstring for plus
    
    :param a: Description
    :type a: int
    :param b: Description
    :type b: int
    :return: Description
    :rtype: int
    """
    return a + b

def minus(a: int, b: int) -> int:
    """
    Docstring for minus
    
    :param a: Description
    :type a: int
    :param b: Description
    :type b: int
    :return: Description
    :rtype: int
    """
    return a - b

def multiply(a: int, b: int) -> int:
    """
    Docstring for multiply
    
    :param a: Description
    :type a: int
    :param b: Description
    :type b: int
    :return: Description
    :rtype: int
    """
    return a * b

def divide(a: int, b: int) -> float:
    """
    Docstring for divide
    
    :param a: Description
    :type a: int
    :param b: Description
    :type b: int
    :return: Description
    :rtype: float
    """
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b

def mod(a: int, b: int) -> int:
    """
    Calculate modulus of two numbers.
    
    :param a: First number
    :type a: int
    :param b: Second number  
    :type b: int
    :return: Modulus result
    :rtype: int
    """
    if b == 0:
        raise ValueError("Modulus by zero is not allowed.")
    return a % b

# Create aliases for backwards compatibility
add = plus
subtract = minus