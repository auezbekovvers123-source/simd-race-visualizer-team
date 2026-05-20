# Person 6 — Results, chart, exports, education

**Owner:** (add your @GitHub in TEAM.md)

**Files:**

| File | Purpose |
|------|---------|
| `education.py` | SIMD/SSE/AVX explanation + scalar/SIMD pseudocode |
| `benchmark.py` | `BenchmarkEngine` — NumPy scalar loop vs vectorized timing |
| `results.py` | `ResultsPanel` — bar chart, speedup badge, CPU diagram |
| `export.py` | CSV export, chart PNG, window screenshot (BMP) |

**Integration:** Person 1 calls `ResultsPanel.finish_race()` after the animation and wires export buttons to `person6.export`.
