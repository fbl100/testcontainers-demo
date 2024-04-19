

from random import Random

from testcontainers_demo.string_utils import generate_random_string


def test_generate_random_string():
    
    rng = Random(0)
    s = generate_random_string(rng)
    assert s == "mynbiqpmzjplsgqejeyd"
