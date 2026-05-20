"""
Demo for the Person 3 benchmark module.

This file shows how to compare a scalar Python function with a NumPy
vectorized function that represents SIMD-style processing.
"""

import numpy as np

from person3.benchmark import compare_functions


def scalar_square_sum(data):
    """Calculate the sum of squares one value at a time."""
    total = 0.0

    # Scalar code processes one number during each loop step.
    for value in data:
        total += value * value

    return total


def simd_square_sum(data):
    """Calculate the sum of squares using NumPy vectorized operations."""
    # NumPy works on the whole array at once, similar to SIMD-style processing.
    return np.sum(data * data)


def main():
    """Generate data, run the benchmark, and print the results."""
    # Use a fixed seed so the random data is the same each time we run the demo.
    random_generator = np.random.default_rng(seed=42)

    # Create sample random data for both functions to process.
    data = random_generator.random(100_000)

    # Compare the scalar function with the SIMD-style function.
    results = compare_functions(scalar_square_sum, simd_square_sum, data)

    scalar_time = results["scalar"]["execution_time"]
    simd_time = results["simd"]["execution_time"]
    speedup = results["speedup"]

    print("Scalar vs SIMD Benchmark Demo")
    print("-----------------------------")
    print(f"Data size: {len(data):,} numbers")
    print(f"Scalar result: {results['scalar']['result']:.4f}")
    print(f"SIMD-style result: {results['simd']['result']:.4f}")
    print()
    print(f"Scalar execution time: {scalar_time:.6f} seconds")
    print(f"SIMD-style execution time: {simd_time:.6f} seconds")
    print(f"Speedup: {speedup:.2f}x")


if __name__ == "__main__":
    main()
