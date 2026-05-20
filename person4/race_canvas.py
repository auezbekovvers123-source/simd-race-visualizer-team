"""
Canvas rendering helpers for the SIMD vs Scalar race visualization.

This module is intentionally the only place that imports Tkinter canvas types.
"""

from __future__ import annotations

from tkinter import Canvas

from person1.config import THEME
from person2.race_model import RaceFrameState, ceil_div


class RaceCanvasDrawer:
    """Draw scalar/SIMD grids and a dual-lane race track on a Tkinter Canvas."""

    DISPLAY_COLS = 20

    def __init__(self, cell_size: int = 18, grid_cols: int = 16) -> None:
        self.cell_size = max(8, int(cell_size))
        self.grid_cols = max(4, int(grid_cols))
        self.pad = 12

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def progress_fractions(self, state: RaceFrameState, n: int) -> tuple[float, float]:
        """Compute scalar/simd normalized progress from a frame state."""
        if n <= 0:
            return 0.0, 0.0
        scalar_frac = self._clamp01(state.scalar_elems / n)
        simd_frac = self._clamp01(state.simd_elems / n)
        return scalar_frac, simd_frac

    def draw_frame(self, canvas: Canvas, state: RaceFrameState, n: int, width: int) -> None:
        """Convenience method to draw both grids and racetrack for one state."""
        scalar_frac, simd_frac = self.progress_fractions(state, n)
        self.draw_grids(canvas, state, n, width)
        self.draw_track(canvas, scalar_frac, simd_frac, width)

    def draw_grids(self, canvas: Canvas, state: RaceFrameState, n: int, width: int) -> None:
        """
        Draw windowed scalar + SIMD element grids (fits on screen for large N).
        """
        canvas.delete("all")
        w = max(1, int(width))
        n = max(1, int(n))
        cw = max(520, int(canvas.winfo_width() or 520))

        cols = min(self.DISPLAY_COLS, max(4, n))
        cell_w = min(24, (cw - 80) // max(cols, 1))
        gap = 3

        def window_start(done: int) -> int:
            half = cols // 2
            return max(0, min(n - cols, done - half))

        def title(y: int, text: str, color: str) -> None:
            canvas.create_text(12, y, text=text, fill=color, anchor="w", font=("Segoe UI", 9, "bold"), tags=("grids",))

        y_scalar = 10
        title(y_scalar, "Scalar (one index at a time)", THEME["scalar"])
        base_y = y_scalar + 16
        scalar_active = max(0, min(n - 1, state.scalar_elems - 1))
        s_start = window_start(scalar_active)

        for j in range(cols):
            idx = s_start + j
            x0 = 24 + j * (cell_w + gap)
            active = idx == scalar_active and state.scalar_elems > 0
            fill = THEME["accent"] if active else THEME["panel"]
            outline = THEME["scalar"] if active else THEME["muted"]
            ow = 3 if active else 1
            canvas.create_rectangle(
                x0,
                base_y,
                x0 + cell_w,
                base_y + cell_w,
                fill=fill,
                outline=outline,
                width=ow,
                tags=("grids",),
            )
            canvas.create_text(
                x0 + cell_w / 2,
                base_y + cell_w / 2,
                text=str(idx),
                fill="#0b1220" if active else THEME["text"],
                font=("Consolas", 8, "bold" if active else "normal"),
                tags=("grids",),
            )

        y_simd = base_y + cell_w + 14
        title(y_simd, f"SIMD ({w}-wide parallel lanes)", THEME["simd"])
        grid_top = y_simd + 16
        simd_chunk = ceil_div(max(state.simd_elems, 1), w) - 1 if state.simd_elems > 0 else 0
        base_index = simd_chunk * w
        s2 = window_start(base_index)

        for r in range(w):
            row_y = grid_top + r * (cell_w + gap)
            for j in range(cols):
                idx = s2 + j
                x0 = 24 + j * (cell_w + gap)
                in_chunk = base_index <= idx < min(n, base_index + w)
                active = in_chunk and state.simd_elems > 0
                fill = THEME["simd"] if active else THEME["panel"]
                outline = "#b8ffd0" if active else THEME["muted"]
                ow = 3 if active else 1
                canvas.create_rectangle(
                    x0,
                    row_y,
                    x0 + cell_w,
                    row_y + cell_w,
                    fill=fill,
                    outline=outline,
                    width=ow,
                    tags=("grids",),
                )
                canvas.create_text(
                    x0 + cell_w / 2,
                    row_y + cell_w / 2,
                    text=str(idx),
                    fill="#061018" if active else THEME["muted"],
                    font=("Consolas", 7, "bold" if active else "normal"),
                    tags=("grids",),
                )

        canvas.create_text(
            cw - 8,
            grid_top + w * (cell_w + gap) + 4,
            text=f"Window: {cols} of N={n:,}",
            fill=THEME["muted"],
            anchor="ne",
            font=("Segoe UI", 8),
            tags=("grids",),
        )

    def draw_track(self, canvas: Canvas, scalar_frac: float, simd_frac: float, width: int) -> None:
        """Draw a two-lane racetrack with moving cars (fits the visible canvas height)."""
        canvas.delete("all")
        scalar_frac = self._clamp01(scalar_frac)
        simd_frac = self._clamp01(simd_frac)

        cw = max(400, int(canvas.winfo_width() or 400))
        ch = max(120, int(canvas.winfo_height() or 120))

        margin_l, margin_r = 32, 32
        lane_h = min(44, max(30, (ch - 52) // 3))
        gap = 10
        lane_top = 28
        lane_w = cw - margin_l - margin_r
        finish_x = margin_l + lane_w - 6
        car_w, car_h = 44, 22
        max_x = max(10, lane_w - car_w - 12)

        pct_s = int(scalar_frac * 100)
        pct_v = int(simd_frac * 100)
        canvas.create_text(
            cw / 2,
            10,
            text=f"RACE  ·  width {max(1, int(width))}  ·  scalar {pct_s}%  ·  SIMD {pct_v}%",
            fill=THEME["text"],
            font=("Segoe UI", 10, "bold"),
            tags=("track",),
        )

        for y0, label, col in (
            (lane_top, "Scalar lane", THEME["scalar"]),
            (lane_top + lane_h + gap, "SIMD lane", THEME["simd"]),
        ):
            y1 = y0 + lane_h
            canvas.create_rectangle(
                margin_l,
                y0,
                margin_l + lane_w,
                y1,
                fill=THEME.get("track_lane", "#0f1724"),
                outline="#2f3d5a",
                width=2,
                tags=("track",),
            )
            for dash in range(0, lane_w, 26):
                canvas.create_line(
                    margin_l + dash,
                    (y0 + y1) / 2,
                    margin_l + dash + 14,
                    (y0 + y1) / 2,
                    fill="#2a3550",
                    width=2,
                    tags=("track",),
                )
            canvas.create_text(
                margin_l,
                y0 - 12,
                anchor="w",
                text=label,
                fill=col,
                font=("Segoe UI", 9, "bold"),
                tags=("track",),
            )

        canvas.create_line(
            finish_x,
            lane_top - 4,
            finish_x,
            lane_top + 2 * lane_h + gap + 4,
            fill="#f0f0f0",
            width=4,
            tags=("track",),
        )

        sx = margin_l + 8 + max_x * scalar_frac
        vx = margin_l + 8 + max_x * simd_frac
        self._draw_car_body(
            canvas, sx, lane_top + lane_h / 2, car_w, car_h, THEME.get("scalar_hot", THEME["scalar"])
        )
        self._draw_car_body(canvas, vx, lane_top + lane_h + gap + lane_h / 2, car_w, car_h, THEME["simd"])

    @staticmethod
    def _draw_car_body(
        canvas: Canvas,
        x: float,
        y_mid: float,
        body_w: int,
        body_h: int,
        color: str,
    ) -> None:
        x0, y0 = x, y_mid - body_h / 2
        x1, y1 = x + body_w, y_mid + body_h / 2
        canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="#0b1220", width=2, tags=("track",))
        wr, wy = 5, y1 - 2
        canvas.create_oval(x0 + 4 - wr, wy - wr, x0 + 4 + wr, wy + wr, fill="#111", outline="#333", tags=("track",))
        canvas.create_oval(x1 - 4 - wr, wy - wr, x1 - 4 + wr, wy + wr, fill="#111", outline="#333", tags=("track",))
