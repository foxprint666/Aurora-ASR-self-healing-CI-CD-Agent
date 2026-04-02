def factorial(n):
    if n == 0:
        return 1
    res = 1
    # Bug: range(1, n) misses the last value. Should be range(1, n+1)
    for i in range(1, n):
        res *= i
    return res

def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True
