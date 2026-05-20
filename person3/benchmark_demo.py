
import numpy as np

try:
    from person3.benchmark import compare_functions
except ModuleNotFoundError:
    from benchmark import compare_functions


def scalar_square_sum(data):
    total = 0.0

    # Scalar code processes one number during each loop step.
    for value in data:
        total += value * value

    return total


def simd_square_sum(data):
    return np.sum(data * data)


def main():
    random_generator = np.random.default_rng(seed=42)

    data = random_generator.random(100_000)

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
    main()git add .