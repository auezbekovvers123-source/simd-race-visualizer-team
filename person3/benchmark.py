"""
Simple benchmark helpers for Person 3.

These functions compare a scalar function with a SIMD/vectorized function by
measuring how long each function takes to run on the same data.
"""

import time


def benchmark(function, data):
    """Run one function with data and return its result and execution time."""
    # Record the time right before the function starts.
    start_time = time.perf_counter()

    # Run the function and save whatever it returns.
    result = function(data)

    # Record the time right after the function finishes.
    end_time = time.perf_counter()

    # The elapsed time is the difference between the end and start times.
    execution_time = end_time - start_time

    return {
        "result": result,
        "execution_time": execution_time,
    }


def compare_functions(scalar_function, simd_function, data):
    """Compare scalar and SIMD functions and return timing results."""
    # Measure the scalar function first.
    scalar_result = benchmark(scalar_function, data)

    # Measure the SIMD/vectorized function with the same data.
    simd_result = benchmark(simd_function, data)

    scalar_time = scalar_result["execution_time"]
    simd_time = simd_result["execution_time"]

    # Speedup tells us how many times faster SIMD is than scalar.
    if simd_time == 0:
        speedup = float("inf")
    else:
        speedup = scalar_time / simd_time

    return {
        "scalar": scalar_result,
        "simd": simd_result,
        "speedup": speedup,
    }
