def gcd(a, b):
    """Compute the greatest common divisor of a and b using the Euclidean algorithm."""
    while b:
        a, b = b, a % b
    return a
