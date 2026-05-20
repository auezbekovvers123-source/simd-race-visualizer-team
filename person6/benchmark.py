"""
NumPy timing engine — Person 6 (results module).

Note: Person 3 may later own `person3/benchmark.py`; integration can switch imports.
"""

from __future__ import annotations

import time
from typing import Tuple

import numpy as np

OperationKey = str


def _pick_repeats(n: int, scalar: bool) -> int:
    """Repeat counts so benchmarks finish quickly but stay measurable."""
    if scalar:
        if n <= 256:
            return 400
        if n <= 4096:
            return 80
        if n <= 65536:
            return 8
        return 2
    if n <= 4096:
        return 2000
    if n <= 65536:
        return 500
    return 120


class BenchmarkEngine:
    """Measure pure-Python scalar loops vs NumPy vector-style expressions."""

    def measure(self, n: int, op: OperationKey) -> Tuple[float, float]:
        """Return (t_scalar_seconds, t_vector_seconds)."""
        if op == "add":
            return self._bench_add(n)
        if op == "mul":
            return self._bench_mul(n)
        return self._bench_dot(n)

    def _bench_add(self, n: int) -> Tuple[float, float]:
        a = np.random.rand(n).astype(np.float64)
        b = np.random.rand(n).astype(np.float64)
        c = np.empty_like(a)
        rs, rv = _pick_repeats(n, True), _pick_repeats(n, False)
        t0 = time.perf_counter()
        for _ in range(rs):
            for i in range(n):
                c[i] = a[i] + b[i]
        t_scalar = (time.perf_counter() - t0) / rs
        t0 = time.perf_counter()
        for _ in range(rv):
            c = a + b
        t_vec = (time.perf_counter() - t0) / rv
        _ = c.nbytes
        return t_scalar, t_vec

    def _bench_mul(self, n: int) -> Tuple[float, float]:
        a = np.random.rand(n).astype(np.float64)
        b = np.random.rand(n).astype(np.float64)
        c = np.empty_like(a)
        rs, rv = _pick_repeats(n, True), _pick_repeats(n, False)
        t0 = time.perf_counter()
        for _ in range(rs):
            for i in range(n):
                c[i] = a[i] * b[i]
        t_scalar = (time.perf_counter() - t0) / rs
        t0 = time.perf_counter()
        for _ in range(rv):
            c = a * b
        t_vec = (time.perf_counter() - t0) / rv
        _ = c.nbytes
        return t_scalar, t_vec

    def _bench_dot(self, n: int) -> Tuple[float, float]:
        a = np.random.rand(n).astype(np.float64)
        b = np.random.rand(n).astype(np.float64)
        rs, rv = _pick_repeats(n, True), _pick_repeats(n, False)
        acc = 0.0
        t0 = time.perf_counter()
        for _ in range(rs):
            s = 0.0
            for i in range(n):
                s += float(a[i] * b[i])
            acc += s
        t_scalar = (time.perf_counter() - t0) / rs
        t0 = time.perf_counter()
        out = 0.0
        for _ in range(rv):
            out += float(np.dot(a, b))
        t_vec = (time.perf_counter() - t0) / rv
        _ = acc + out
        return t_scalar, t_vec
