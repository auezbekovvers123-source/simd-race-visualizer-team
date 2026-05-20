
**Owner:** TBD (add GitHub @ in TEAM.md)


**Planned:** `benchmark.py` — `BenchmarkEngine`, NumPy scalar vs vectorized timing.
This module provides simple benchmark helpers for comparing a scalar function
with a SIMD/vectorized function.

The main file is:



## Purpose of Benchmarking

Benchmarking measures how long code takes to run. In this project, it helps us
compare:

- **Scalar code**: processes one value at a time
- **SIMD/vectorized code**: processes multiple values more efficiently

## How Speedup Is Calculated

Speedup shows how many times faster the SIMD version is:

```text
speedup = scalar_time / simd_time
```

Example:

```text
scalar_time = 0.020 seconds
simd_time   = 0.005 seconds
speedup     = 4.0x
```

This means the SIMD version was about 4 times faster.

## Why `time.perf_counter()` Is Used

`time.perf_counter()` is used because it gives accurate timing for short code
measurements. It is better for benchmarks than regular clock time.

## Example Benchmark Output

```python
{
    "scalar": {"result": 55, "execution_time": 0.000012},
    "simd": {"result": 55, "execution_time": 0.000004},
    "speedup": 3.0
}
```

## Example Usage

```python
from person3.benchmark import compare_functions


def scalar_sum(data):
    total = 0
    for value in data:
        total += value
    return total


def simd_sum(data):
    return sum(data)


data = [1, 2, 3, 4, 5]
results = compare_functions(scalar_sum, simd_sum, data)

print(results)
```



- The benchmark runs a function and records how long it takes.
- The same input data should be used for both scalar and SIMD functions.
- A higher speedup means the SIMD/vectorized function is faster.
- Benchmark times can change slightly each time the program runs.