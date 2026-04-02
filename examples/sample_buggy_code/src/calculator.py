"""
Sample buggy calculator module.
Contains intentional bugs for the agent to fix.
"""

def add(a, b):
    """Add two numbers - BUG: missing b in operation"""
    return a + c  # c is undefined!

def subtract(a, b):
    """Subtract two numbers"""
    return a - b

def multiply(a, b):
    """Multiply two numbers - BUG: Wrong variable name"""
    return a * x  # x is undefined!

def divide(a, b):
    """Divide two numbers - BUG: No zero check"""
    return a / b  # Will fail when b=0

def power(a, b):
    """Raise a to power b"""
    return a ** b