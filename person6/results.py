"""
Results panel: benchmarks, bar chart, speedup badge, CPU diagram — Person 6.
"""

from __future__ import annotations

import math
from typing import Optional, Tuple

import matplotlib as mpl
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from person1.config import OP_KEY_TO_LABEL, THEME
from person6.benchmark import BenchmarkEngine, OperationKey

mpl.rcParams.update(
    {
        "figure.facecolor": "#121826",
        "axes.facecolor": "#1a2233",
        "axes.edgecolor": "#3d4f6f",
        "axes.labelcolor": "#dbe7ff",
        "axes.titlecolor": "#f2f6ff",
        "text.color": "#dbe7ff",
        "xtick.color": "#c9d6f0",
        "ytick.color": "#c9d6f0",
        "grid.color": "#2f3d5a",
        "grid.alpha": 0.55,
    }
)


class ResultsPanel:
    """
    Post-race measurement UI: NumPy timing, matplotlib chart, winner/speedup labels.

    Person 1 wires this into the main app; export helpers live in person6.export.
    """

    def __init__(self) -> None:
        self._bench = BenchmarkEngine()
        self._measured_scalar: Optional[float] = None
        self._measured_vector: Optional[float] = None
        self._celebrate_step = 0
        self._celebrate_after: Optional[str] = None

        self._fig = Figure(figsize=(5.4, 2.6), dpi=100)
        self._ax = self._fig.add_subplot(111)

    @property
    def figure(self) -> Figure:
        return self._fig

    @property
    def has_measurements(self) -> bool:
        return self._measured_scalar is not None and self._measured_vector is not None

    @property
    def measured_scalar(self) -> Optional[float]:
        return self._measured_scalar

    @property
    def measured_vector(self) -> Optional[float]:
        return self._measured_vector

    def clear_measurements(self) -> None:
        self._measured_scalar = None
        self._measured_vector = None
        self._celebrate_step = 0

    def speedup(self) -> float:
        if self._measured_scalar is None or self._measured_vector is None:
            return 0.0
        if self._measured_vector <= 0:
            return 0.0
        return self._measured_scalar / self._measured_vector

    def finish_race(
        self,
        root: tk.Misc,
        *,
        n: int,
        op: OperationKey,
        width: int,
        result_label: tk.Label,
        winner_banner: tk.Label,
        speedup_badge: tk.Label,
        canvas_mpl: FigureCanvasTkAgg,
        scroll_canvas: Optional[tk.Canvas] = None,
    ) -> Tuple[float, float]:
        """Run benchmarks and update labels, chart, and celebration."""
        result_label.config(text="Measuring with NumPy (scalar Python loop vs vectorized)…")
        root.update_idletasks()

        ts, tv = self._bench.measure(n, op)
        self._measured_scalar = ts
        self._measured_vector = tv
        speed = self.speedup()

        op_name = OP_KEY_TO_LABEL.get(op, op)
        result_label.config(
            text=(
                f"{op_name}  |  N={n:,}  |  SIMD model width={width}\n"
                f"Measured scalar: {ts * 1000:.3f} ms   |   vectorized: {tv * 1000:.3f} ms"
            )
        )
        self.plot_bar(op_name)
        canvas_mpl.draw_idle()

        rounded = min(9999.0, speed) if math.isfinite(speed) else 0.0
        winner_banner.config(text=f"SIMD wins!  ~{rounded:.1f}x faster (NumPy vs Python loop)")
        speedup_badge.config(text=f"SPEEDUP: {rounded:.2f}x", fg=THEME["accent"], bg="#2a1f05")

        if scroll_canvas is not None:
            scroll_canvas.update_idletasks()
            scroll_canvas.yview_moveto(0.0)

        self._celebrate_step = 0
        self._animate_celebration(root, speedup_badge)
        return ts, tv

    def _animate_celebration(self, root: tk.Misc, speedup_badge: tk.Label) -> None:
        if not self.has_measurements:
            self._celebrate_after = None
            return
        if self._celebrate_step >= 14:
            self._celebrate_after = None
            return
        self._celebrate_step += 1
        sp = self.speedup()
        alt = self._celebrate_step % 2 == 0
        speedup_badge.config(
            fg=THEME["simd"] if alt else THEME["accent"],
            bg="#1f2a18" if alt else "#2a1f05",
            text=f"SPEEDUP: {sp:.2f}x",
        )
        self._celebrate_after = root.after(160, lambda: self._animate_celebration(root, speedup_badge))

    def plot_bar(self, title_suffix: str) -> None:
        """Render scalar vs vectorized bar chart."""
        if not self.has_measurements:
            return
        ts, tv = self._measured_scalar, self._measured_vector
        ax = self._ax
        ax.clear()
        ax.set_facecolor("#1a2233")
        labels = ["Scalar\n(Python loop)", "Vectorized\n(NumPy)"]
        vals = [ts * 1000, tv * 1000]
        colors = [THEME["scalar"], THEME["simd"]]
        ax.bar(labels, vals, color=colors, edgecolor="#0b1220", linewidth=1.4, width=0.55)
        ax.set_ylabel("Time (ms)")
        ax.set_title(f"Measured on your machine — {title_suffix}", pad=12)
        vmax = max(vals) if vals else 1.0
        for i, v in enumerate(vals):
            ax.text(i, v + vmax * 0.03, f"{v:.3f} ms", ha="center", fontsize=10, color="#f2f6ff")
        ax.grid(axis="y", linestyle="--", alpha=0.45)
        ax.set_axisbelow(True)
        self._fig.tight_layout()

    @staticmethod
    def draw_arch_diagram(arch_canvas: tk.Canvas) -> None:
        """Simplified CPU block diagram (where SIMD units live)."""
        cv = arch_canvas
        cv.delete("all")
        w = int(cv.winfo_width() or 800)

        def box(x1: float, y1: float, x2: float, y2: float, text: str, fill: str, outline: str) -> None:
            cv.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=2)
            cv.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=text, font=("Segoe UI", 9, "bold"), fill="#0b1220")

        cv.create_text(
            12, 10, anchor="w", text="Where SIMD lives (simplified)", font=("Segoe UI", 10, "bold"), fill=THEME["text"]
        )
        x0, y0, bw, bh = 18, 30, max(120, (w - 70) // 4), 74
        titles = [
            ("Front-end\n(fetch/decode)", "#dbe7ff", "#2f3d5a"),
            ("Scalar\nALUs", "#dbe7ff", "#2f3d5a"),
            ("Load/Store\n+ caches", "#dbe7ff", "#2f3d5a"),
            ("SIMD / FPU\n(SSE/AVX)", "#ffd36a", "#6b4b16"),
        ]
        for i, (title, fill, outline) in enumerate(titles):
            box(x0 + i * (bw + 12), y0, x0 + i * (bw + 12) + bw, y0 + bh, title, fill, outline)
