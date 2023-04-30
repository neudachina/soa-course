import time
import sys

from .object import Object

CYCLES = 1000


def time_testing(function, obj):
    start = time.monotonic_ns()
    for _ in range(CYCLES):
        function(obj)
    end = time.monotonic_ns()
    return (end - start) / CYCLES / 100000


def test(serialization_function, deserialization_function, test_name):
    testing_object = Object()
    testing_object.create_default()
    serialized = serialization_function(testing_object)
    return f"{test_name} - " \
           f"{sys.getsizeof(serialized)} – " \
           f"{time_testing(serialization_function, testing_object)} – " \
           f"{time_testing(deserialization_function, serialized)}\n"
