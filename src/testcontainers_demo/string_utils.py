import string
from random import Random

def generate_random_string(rng: Random, length=20):
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase
    return ''.join(rng.choice(letters) for _ in range(length))
