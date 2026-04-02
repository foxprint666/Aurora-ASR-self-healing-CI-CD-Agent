import pytest
from src.math_utils import factorial, is_prime

def test_factorial():
    assert factorial(5) == 120

def test_is_prime():
    assert is_prime(7) == True
    assert is_prime(4) == False
