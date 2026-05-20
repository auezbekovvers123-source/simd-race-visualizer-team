"""
Education text and pseudocode — Person 6.
"""

from __future__ import annotations

from person1.config import OP_KEY_TO_LABEL

OperationKey = str  # "add" | "mul" | "dot"


def education_text(width: int, isa: str) -> str:
    """Explain SIMD, SSE/AVX, and why speedup happens."""
    return (
        "What is SIMD?\n"
        "SIMD (Single Instruction, Multiple Data) applies one instruction to several "
        "data elements at once — like a conveyor belt carrying multiple boxes through "
        "the same machine step. A scalar loop visits one element per iteration; SIMD "
        "visits a whole small batch per instruction.\n\n"
        f"What are SSE / AVX?\n"
        "SSE (Streaming SIMD Extensions) historically processed 128-bit vectors — "
        "commonly 4 single-precision floats at a time. AVX widened registers to 256 bits "
        f"(often 8 floats). This demo uses width {width} to stand in for {isa}.\n\n"
        "Why is vectorized code faster?\n"
        "1) Fewer loop iterations and less per-element overhead.\n"
        "2) CPUs expose dedicated vector execution units.\n"
        "3) Memory bandwidth is amortized across lanes.\n"
        "Real speedups depend on N, alignment, and whether the loop is compute- or memory-bound.\n"
    )


def pseudocode_scalar(op: OperationKey) -> str:
    """Scalar pseudocode for the selected operation."""
    if op == "add":
        return "# Scalar vector add\nfor i in range(n):\n    c[i] = a[i] + b[i]\n"
    if op == "mul":
        return "# Scalar element-wise multiply\nfor i in range(n):\n    c[i] = a[i] * b[i]\n"
    return "# Scalar dot product\nsum = 0.0\nfor i in range(n):\n    sum += a[i] * b[i]\n"


def pseudocode_simd(op: OperationKey, width: int) -> str:
    """SIMD-style pseudocode for the selected operation."""
    w = str(width)
    if op == "add":
        return (
            f"# SIMD vector add ({w}-wide)\n"
            "for chunk in range(0, n, WIDTH):\n"
            "    va = load a[chunk:chunk+WIDTH]\n"
            "    vb = load b[chunk:chunk+WIDTH]\n"
            "    vc = va + vb\n"
            "    store c[chunk:chunk+WIDTH] = vc\n"
        ).replace("WIDTH", w)
    if op == "mul":
        return (
            f"# SIMD multiply ({w}-wide)\n"
            "for chunk in range(0, n, WIDTH):\n"
            "    va = load a[chunk:chunk+WIDTH]\n"
            "    vb = load b[chunk:chunk+WIDTH]\n"
            "    vc = va * vb\n"
            "    store c[chunk:chunk+WIDTH] = vc\n"
        ).replace("WIDTH", w)
    return (
        f"# SIMD dot ({w}-wide sketch)\n"
        "partial = vector_zeros()\n"
        "for chunk in range(0, n, WIDTH):\n"
        "    va = load a[chunk:chunk+WIDTH]\n"
        "    vb = load b[chunk:chunk+WIDTH]\n"
        "    partial += va * vb\n"
        "sum = horizontal_add(partial)\n"
    ).replace("WIDTH", w)


def full_education_panel(op: OperationKey, width: int) -> str:
    """Combined panel text for the education Text widget."""
    isa = "SSE (128-bit class)" if width == 4 else "AVX (256-bit class)"
    label = OP_KEY_TO_LABEL.get(op, op)
    return (
        f"Operation: {label}\n\n"
        + education_text(width, isa)
        + "\n--- Scalar pseudocode ---\n"
        + pseudocode_scalar(op)
        + "\n--- SIMD pseudocode ---\n"
        + pseudocode_simd(op, width)
    )
