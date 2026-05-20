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


def why_scalar_slower_text(width: int, op: OperationKey | None = None) -> str:
    """
    Plain-language explanation for the Learn tab: why scalar loses to SIMD.
    """
    w = max(1, int(width))
    op_name = OP_KEY_TO_LABEL.get(op, "your operation") if op else "your operation"
    isa = "SSE-style (4 numbers at once)" if w == 4 else "AVX-style (8 numbers at once)"
    chunks = "N ÷ 4" if w == 4 else "N ÷ 8"

    return (
        "Why is scalar slower than SIMD?\n"
        "================================\n\n"
        "Think of two workers packing boxes on a conveyor belt.\n\n"
        "  • SCALAR worker: picks up ONE box, processes it, puts it down, "
        "then walks back and repeats for the next box.\n"
        f"  • SIMD worker: picks up {w} boxes at the same time, does the same step "
        f"on all {w}, then moves to the next group.\n\n"
        "Same total work (N items), but the SIMD worker needs far fewer trips.\n\n"
        "What you see in this app\n"
        "------------------------\n"
        "  • Top grids: scalar highlights one index at a time; SIMD lights a whole "
        f"{w}-wide chunk each step.\n"
        "  • Racetrack: both start together, but SIMD's car reaches the finish in "
        f"fewer ticks (about {chunks} as many steps for large N).\n"
        "  • Results tab: after the race we time a real Python loop (scalar) vs "
        "NumPy vector code (SIMD-like) for the same array size.\n\n"
        "Three simple reasons scalar is slower\n"
        "-----------------------------------\n"
        "1) More loop trips\n"
        f"   Scalar runs about N steps. SIMD runs about N/{w} steps "
        f"(each step handles {w} elements).\n\n"
        "2) Extra work per element\n"
        "   A Python for-loop does index math, bounds checks, and dispatch "
        "every single time. SIMD-style code does one bulk operation on many "
        "values (less overhead per item).\n\n"
        "3) The CPU has special wide units\n"
        f"   Modern CPUs have vector units built for {isa}. "
        "Scalar code often uses the regular ALU one value at a time; "
        "vectorized code can feed those wide units so the hardware works "
        "as designed.\n\n"
        f"Your current settings: {op_name}, SIMD width = {w}\n\n"
        "Important honesty note\n"
        "----------------------\n"
        f"You will not always get exactly {w}× speedup. Memory speed, cache, "
        "and how data is laid out in RAM also matter. This demo uses simple "
        f"loops and NumPy so the difference is easy to see in class — not "
        f"every real program is a perfect {w}× win.\n\n"
        "One sentence for your defense\n"
        "-----------------------------\n"
        f"Scalar is slower because it completes the job in ~N serial steps, "
        f"while SIMD completes the same job in ~N/{w} wider steps using "
        "hardware that processes multiple data values per instruction."
    )


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
