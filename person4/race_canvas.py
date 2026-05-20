"""
Canvas rendering helpers for the SIMD vs Scalar race visualization.

This module is intentionally the only place that imports Tkinter canvas types.
"""

from __future__ import annotations

from tkinter import Canvas

from person1.config import THEME
from person2.race_model import RaceFrameState


class RaceCanvasDrawer:
    """Draw scalar/SIMD grids and a dual-lane race track on a Tkinter Canvas."""

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
        Draw scalar and SIMD activity grids.

        Scalar: one highlighted cell.
        SIMD: one highlighted chunk column across `width` parallel rows.
        """
        canvas.delete("grids")
        w = max(1, int(width))
        n = max(1, int(n))

        x0 = self.pad
        y0 = self.pad
        scalar_rows = max(1, (n + self.grid_cols - 1) // self.grid_cols)
        scalar_active = max(0, min(n - 1, state.scalar_elems - 1))
        self._draw_scalar_grid(canvas, x0, y0, n, scalar_rows, scalar_active)

        grid_w = self.grid_cols * self.cell_size
        gap = self.pad * 2
        simd_y0 = y0
        simd_x0 = x0 + grid_w + gap
        simd_cols = max(1, (n + w - 1) // w)
        simd_active_col = max(0, min(simd_cols - 1, (max(0, state.simd_elems - 1)) // w))
        self._draw_simd_grid(canvas, simd_x0, simd_y0, simd_cols, w, simd_active_col)

    def draw_track(self, canvas: Canvas, scalar_frac: float, simd_frac: float, width: int) -> None:
        """Draw a two-lane racetrack and place scalar/SIMD cars by progress fractions."""
        canvas.delete("track")
        scalar_frac = self._clamp01(scalar_frac)
        simd_frac = self._clamp01(simd_frac)

        cw = max(300, int(canvas.winfo_width()))
        ch = max(220, int(canvas.winfo_height()))
        x0 = self.pad
        x1 = cw - self.pad
        top = ch - 90
        lane_h = 26
        lane_gap = 12

        canvas.create_text(
            x0,
            top - 18,
            anchor="w",
            text=f"Race Track (SIMD x{max(1, int(width))})",
            fill=THEME["text"],
            tags=("track",),
        )

        self._draw_lane(canvas, x0, top, x1, lane_h, "Scalar", THEME["scalar"])
        self._draw_lane(
            canvas,
            x0,
            top + lane_h + lane_gap,
            x1,
            lane_h,
            "SIMD",
            THEME["simd"],
        )

        self._draw_car(canvas, x0, x1, top, lane_h, scalar_frac, THEME["scalar"], "S")
        self._draw_car(
            canvas,
            x0,
            x1,
            top + lane_h + lane_gap,
            lane_h,
            simd_frac,
            THEME["simd"],
            "V",
        )

    def _draw_scalar_grid(
        self,
        canvas: Canvas,
        x0: int,
        y0: int,
        n: int,
        rows: int,
        active_idx: int,
    ) -> None:
        canvas.create_text(
            x0,
            y0 - 8,
            anchor="sw",
            text="Scalar",
            fill=THEME["text"],
            tags=("grids",),
        )
        for idx in range(n):
            row = idx // self.grid_cols
            col = idx % self.grid_cols
            if row >= rows:
                break
            x1 = x0 + col * self.cell_size
            y1 = y0 + row * self.cell_size
            fill = THEME["accent"] if idx == active_idx else THEME["panel"]
            outline = THEME["scalar"] if idx == active_idx else THEME["muted"]
            canvas.create_rectangle(
                x1,
                y1,
                x1 + self.cell_size - 2,
                y1 + self.cell_size - 2,
                fill=fill,
                outline=outline,
                width=1,
                tags=("grids",),
            )

    def _draw_simd_grid(
        self,
        canvas: Canvas,
        x0: int,
        y0: int,
        cols: int,
        width: int,
        active_col: int,
    ) -> None:
        canvas.create_text(
            x0,
            y0 - 8,
            anchor="sw",
            text=f"SIMD ({width}-wide)",
            fill=THEME["text"],
            tags=("grids",),
        )
        for r in range(width):
            for c in range(cols):
                x1 = x0 + c * self.cell_size
                y1 = y0 + r * self.cell_size
                is_active = c == active_col
                fill = THEME["accent"] if is_active else THEME["panel"]
                outline = THEME["simd"] if is_active else THEME["muted"]
                canvas.create_rectangle(
                    x1,
                    y1,
                    x1 + self.cell_size - 2,
                    y1 + self.cell_size - 2,
                    fill=fill,
                    outline=outline,
                    width=1,
                    tags=("grids",),
                )

    def _draw_lane(
        self,
        canvas: Canvas,
        x0: int,
        y0: int,
        x1: int,
        lane_h: int,
        label: str,
        color: str,
    ) -> None:
        canvas.create_rectangle(
            x0,
            y0,
            x1,
            y0 + lane_h,
            fill=THEME["panel"],
            outline=THEME["muted"],
            width=1,
            tags=("track",),
        )
        canvas.create_line(
            x1 - 16,
            y0,
            x1 - 16,
            y0 + lane_h,
            fill=THEME["accent"],
            width=2,
            tags=("track",),
        )
        canvas.create_text(
            x0 + 6,
            y0 + lane_h / 2,
            anchor="w",
            text=label,
            fill=color,
            tags=("track",),
        )

    def _draw_car(
        self,
        canvas: Canvas,
        x0: int,
        x1: int,
        y0: int,
        lane_h: int,
        frac: float,
        color: str,
        text: str,
    ) -> None:
        left = x0 + 38
        right = x1 - 24
        xpos = left + (right - left) * frac
        half_w = 11
        half_h = lane_h / 2 - 3
        canvas.create_rectangle(
            xpos - half_w,
            y0 + lane_h / 2 - half_h,
            xpos + half_w,
            y0 + lane_h / 2 + half_h,
            fill=color,
            outline=THEME["bg"],
            width=1,
            tags=("track",),
        )
        canvas.create_text(
            xpos,
            y0 + lane_h / 2,
            text=text,
            fill=THEME["bg"],
            tags=("track",),
        )
