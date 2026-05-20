"""
Race controls and animation loop — Person 5.

Mixin-style controller: countdown, continuous/step tick loop, HUD updates, optional sounds.
Uses person2.RaceAnimation for frame math. Drawing is delegated via callbacks (person4).
"""

from __future__ import annotations

import math
import time
import tkinter as tk
from typing import Callable, Optional, Protocol

from person1.config import OP_LABEL_TO_KEY, THEME
from person2.race_model import (
    OperationKey,
    RaceAnimation,
    RaceFrameState,
    ceil_div,
    logical_scalar_cycles,
    logical_simd_cycles,
)

try:
    import winsound

    _HAS_WINSOUND = True
except Exception:  # noqa: BLE001
    winsound = None  # type: ignore[assignment]
    _HAS_WINSOUND = False


RACE_TIPS = [
    "Scalar visits one index per beat; SIMD lights a whole chunk each step.",
    "The racetrack uses tick progress — SIMD reaches the line in fewer ticks (≈ N/width).",
    "Cycles saved = scalar logical cycles − SIMD logical cycles on the teaching model.",
]


class RaceHudWidgets(Protocol):
    """Labels the controller updates each frame."""

    scalar_hud: tk.Label
    simd_hud: tk.Label
    cycles_saved_label: tk.Label
    delta_label: tk.Label
    tip_label: tk.Label
    grid_canvas: tk.Canvas
    track_canvas: tk.Canvas


DrawGridsFn = Callable[
    [int, int, int, int, OperationKey, float, float, int],
    None,
]
DrawTrackFn = Callable[[float, float, int], None]
OnRaceFinishFn = Callable[[], None]


class RaceController:
    """
    Run / reset / step race flow with countdown and timer-driven frames.

    Wire into a Tk app by passing HUD widgets and draw callbacks from person4.
    """

    ANIM_FRAMES = 140
    REFRESH_MS = 12
    COUNTDOWN_WORDS = ("3 …", "2 …", "1 …", "GO!")
    SIMD_FLASH_FRAMES = 8

    def __init__(
        self,
        root: tk.Misc,
        *,
        array_size: tk.IntVar,
        operation: tk.StringVar,
        simd_width: tk.IntVar,
        sounds: tk.BooleanVar,
        step_mode: tk.BooleanVar,
        hud: RaceHudWidgets,
        draw_grids: DrawGridsFn,
        draw_track: DrawTrackFn,
        on_race_finish: OnRaceFinishFn,
        anim_frames: int = ANIM_FRAMES,
    ) -> None:
        self._root = root
        self._array_size = array_size
        self._operation = operation
        self._simd_width = simd_width
        self._sounds = sounds
        self._step_mode = step_mode
        self._hud = hud
        self._draw_grids = draw_grids
        self._draw_track = draw_track
        self._on_race_finish = on_race_finish

        self._anim = RaceAnimation(anim_frames)
        self._race_active = False
        self._phase = "idle"
        self._countdown_step = -1
        self._frame_i = 0
        self._after_id: Optional[str] = None
        self._t0_wall: Optional[float] = None
        self._pulse = 0
        self._tip_idx = 0
        self._simd_finish_announced = False
        self._prev_simd_chunk = -1
        self._simd_flash_remaining = 0

    def n(self) -> int:
        return int(self._array_size.get())

    def width(self) -> int:
        return int(self._simd_width.get())

    def op(self) -> OperationKey:
        return OP_LABEL_TO_KEY.get(self._operation.get(), "add")

    def beep(self, freq: int, ms: int) -> None:
        if not self._sounds.get() or not _HAS_WINSOUND or winsound is None:
            return
        try:
            winsound.Beep(freq, ms)
        except Exception:  # noqa: BLE001
            pass

    def cancel_after(self) -> None:
        if self._after_id is not None:
            try:
                self._root.after_cancel(self._after_id)
            except Exception:  # noqa: BLE001
                pass
            self._after_id = None

    def reset(self) -> None:
        """Stop timers and return HUD to idle."""
        self.cancel_after()
        self._race_active = False
        self._phase = "idle"
        self._countdown_step = -1
        self._frame_i = 0
        self._t0_wall = None
        self._pulse = 0
        self._tip_idx = 0
        self._simd_finish_announced = False
        self._prev_simd_chunk = -1
        self._simd_flash_remaining = 0

        self._hud.scalar_hud.config(text="Scalar: idle")
        self._hud.simd_hud.config(text="SIMD: idle")
        self._hud.cycles_saved_label.config(text="Cycles saved (model): —")
        self._hud.delta_label.config(
            text="Live: start a race to see who is ahead on elements processed.",
            fg=THEME["accent"],
        )
        self._hud.tip_label.config(text="Tip: enable Step mode to advance one frame at a time.")
        self._hud.grid_canvas.delete("all")
        self._hud.track_canvas.delete("all")

    def start_race(self) -> None:
        if self._race_active:
            return
        self.reset()
        self._race_active = True
        self._phase = "countdown"
        self._countdown_step = -1
        self._simd_finish_announced = False
        self._countdown_tick()

    def step_once(self) -> None:
        if not self._race_active or self._phase != "race":
            return
        if not self._step_mode.get():
            return
        self._run_single_frame()

    def _countdown_tick(self) -> None:
        self._after_id = None
        if not self._race_active or self._phase != "countdown":
            return

        self._countdown_step += 1
        if self._countdown_step < len(self.COUNTDOWN_WORDS):
            self._draw_countdown_overlay(self.COUNTDOWN_WORDS[self._countdown_step])
            self.beep(700, 40)
            self._after_id = self._root.after(380, self._countdown_tick)
            return

        self._phase = "race"
        self._frame_i = 0
        self._t0_wall = time.perf_counter()
        self.beep(1040, 70)
        if self._step_mode.get():
            self._run_single_frame()
        else:
            self._after_id = self._root.after(self.REFRESH_MS, self._tick)

    def _draw_countdown_overlay(self, word: str) -> None:
        self._hud.track_canvas.delete("all")
        c = self._hud.grid_canvas
        c.delete("all")
        cw = max(520, c.winfo_width())
        ch = max(280, c.winfo_height())
        c.create_rectangle(0, 0, cw, ch, fill="#0b1220", outline="")
        c.create_text(
            cw / 2,
            ch / 2 - 10,
            text=word,
            fill=THEME["accent"],
            font=("Segoe UI", 56, "bold"),
        )
        c.create_text(
            cw / 2,
            ch / 2 + 50,
            text="Same N — SIMD takes wider steps.",
            fill=THEME["muted"],
            font=("Segoe UI", 11),
        )

    def _tick(self) -> None:
        if not self._race_active or self._phase != "race":
            return
        self._run_single_frame()
        if self._race_active and self._phase == "race":
            self._after_id = self._root.after(self.REFRESH_MS, self._tick)

    def _run_single_frame(self) -> None:
        self._pulse += 1
        f = self._frame_i
        n = self.n()
        w = self.width()
        op = self.op()
        F = self._anim.anim_frames

        simd_tick_frac = min(1.0, (f + 1) * w / F)
        scalar_tick_frac = min(1.0, (f + 1) / F)
        simd_ticks_done = max(1, int(math.ceil(F / w)))

        st = self._anim.progress(f, n, w, op)
        self._update_hud(st, n, w, op, f, F, simd_ticks_done, simd_tick_frac, scalar_tick_frac)

        if simd_tick_frac >= 1.0 and scalar_tick_frac < 1.0 and not self._simd_finish_announced:
            self._simd_finish_announced = True
            self.beep(988, 90)

        flash = self._simd_flash_remaining
        self._draw_grids(
            st.scalar_elems,
            st.simd_elems,
            n,
            w,
            op,
            scalar_tick_frac,
            simd_tick_frac,
            flash,
        )
        self._draw_track(scalar_tick_frac, simd_tick_frac, w)

        finished = f >= F and st.scalar_elems >= n
        if finished:
            self._race_active = False
            self._phase = "idle"
            self.cancel_after()
            self.beep(660, 80)
            self._on_race_finish()
            return

        self._frame_i += 1

    def _update_hud(
        self,
        st: RaceFrameState,
        n: int,
        w: int,
        op: OperationKey,
        f: int,
        F: int,
        simd_ticks_done: int,
        simd_tick_frac: float,
        scalar_tick_frac: float,
    ) -> None:
        se, ve, sc, vc = st.scalar_elems, st.simd_elems, st.scalar_cycles, st.simd_cycles

        simd_chunk = ceil_div(max(ve, 1), w) - 1 if ve > 0 else 0
        if simd_chunk != self._prev_simd_chunk:
            self._simd_flash_remaining = self.SIMD_FLASH_FRAMES
            self._prev_simd_chunk = simd_chunk
        if self._simd_flash_remaining > 0:
            self._simd_flash_remaining -= 1

        now = time.perf_counter()
        if self._t0_wall is None:
            self._t0_wall = now
        wall_ms = (now - self._t0_wall) * 1000.0
        tick_ms = float(self.REFRESH_MS)
        scalar_model_ms = (f + 1) * tick_ms
        simd_model_ms = (f + 1) * tick_ms / max(w, 1)

        self._hud.scalar_hud.config(
            text=(
                f"Scalar — model {scalar_model_ms:.1f} ms | wall {wall_ms:.1f} ms | "
                f"tick {f + 1}/{F} | logical cycles {sc:,}/{logical_scalar_cycles(n, op):,} | "
                f"elements {se:,}/{n:,}"
            )
        )
        self._hud.simd_hud.config(
            text=(
                f"SIMD — model {simd_model_ms:.1f} ms | wall {wall_ms:.1f} ms | "
                f"line ~tick {simd_ticks_done} (width {w}) | "
                f"logical cycles {vc:,}/{logical_simd_cycles(n, w, op):,} | "
                f"elements {ve:,}/{n:,}"
            )
        )
        saved = self._anim.cycles_saved(st)
        self._hud.cycles_saved_label.config(
            text=f"Cycles saved (model): {saved:,}  (scalar − SIMD logical cycles)"
        )

        ahead = ve - se
        if ahead > 0:
            pct = 100.0 * ahead / max(n, 1)
            self._hud.delta_label.config(
                text=f"Live: SIMD ahead by {ahead:,} elements (~{pct:.1f}% of N).",
                fg=THEME["simd"],
            )
        elif ahead < 0:
            self._hud.delta_label.config(
                text="Live: scalar briefly ahead — keep watching.",
                fg=THEME["scalar"],
            )
        else:
            self._hud.delta_label.config(text="Live: same element progress.", fg=THEME["accent"])

        if self._pulse % 28 == 0:
            self._tip_idx = (self._tip_idx + 1) % len(RACE_TIPS)
            self._hud.tip_label.config(text=f"Tip: {RACE_TIPS[self._tip_idx]}")
