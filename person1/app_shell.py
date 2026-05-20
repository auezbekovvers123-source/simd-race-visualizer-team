"""
Main Tk window — Person 1 integration shell.

Wires person2 (race model), person4 (canvas), person5 (controller),
person6 (results, education, exports) into one runnable app.
"""

from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from dataclasses import dataclass
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from person1.config import OP_LABEL_TO_KEY, THEME
from person2.race_model import RaceFrameState
from person4.race_canvas import RaceCanvasDrawer
from person5.race_controller import RaceController
from person6.education import why_scalar_slower_text
from person6.export import export_csv, save_chart_png, save_window_screenshot
from person6.results import ResultsPanel


@dataclass
class _RaceHud:
    """HUD widgets passed to RaceController (person5)."""

    scalar_hud: tk.Label
    simd_hud: tk.Label
    cycles_saved_label: tk.Label
    delta_label: tk.Label
    tip_label: tk.Label
    grid_canvas: tk.Canvas
    track_canvas: tk.Canvas


class SimdScalarRaceApp(tk.Tk):
    """Full app: controls, race animation, benchmarks, chart, exports."""

    def __init__(self) -> None:
        super().__init__()
        self.title("SIMD vs Scalar — Race Visualizer")
        self.geometry("1280x920")
        self.minsize(1080, 800)
        self.configure(bg=THEME["bg"])

        self._array_size = tk.IntVar(value=10_000)
        self._operation = tk.StringVar(value="Vector Add")
        self._simd_width = tk.IntVar(value=8)
        self._sounds = tk.BooleanVar(value=True)
        self._step_mode = tk.BooleanVar(value=False)

        self._drawer = RaceCanvasDrawer()
        self._results = ResultsPanel()
        self._last_track: tuple[float, float, int] | None = None

        self._title_font = tkfont.Font(family="Segoe UI", size=20, weight="bold")
        self._subtitle_font = tkfont.Font(family="Segoe UI", size=11)
        self._hud_font = tkfont.Font(family="Segoe UI", size=10)
        self._speedup_font = tkfont.Font(family="Segoe UI", size=28, weight="bold")

        self._configure_styles()
        self._build_ui()
        self._wire_controller()
        self._refresh_learn()

        self._operation.trace_add("write", lambda *_: self._refresh_learn())
        self._simd_width.trace_add("write", lambda *_: self._refresh_learn())
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _configure_styles(self) -> None:
        st = ttk.Style(self)
        try:
            st.theme_use("clam")
        except tk.TclError:
            pass
        bg, panel, fg = THEME["bg"], THEME["panel"], THEME["text"]
        border = THEME["border"]
        st.configure(".", background=bg, foreground=fg)
        st.configure("TFrame", background=bg)
        st.configure(
            "TLabelframe",
            background=panel,
            foreground=THEME["muted"],
            bordercolor=border,
            lightcolor=border,
            darkcolor=border,
        )
        st.configure(
            "TLabelframe.Label",
            background=panel,
            foreground=THEME["muted"],
            font=("Segoe UI", 10, "bold"),
        )
        st.configure("TLabel", background=panel, foreground=fg)
        st.configure("TRadiobutton", background=panel, foreground=fg)
        st.configure("TCheckbutton", background=panel, foreground=fg)
        st.configure("TButton", background="#2c3a59", foreground=fg, padding=(12, 6))
        st.map("TButton", background=[("active", "#3a4d75")])
        st.configure(
            "Accent.TButton",
            background="#3b82f6",
            foreground="#071018",
            font=("Segoe UI", 10, "bold"),
        )
        st.map("Accent.TButton", background=[("active", "#60a5fa")])
        st.configure(
            "Dark.TCombobox",
            fieldbackground="#1a2233",
            background="#2c3a59",
            foreground=THEME["text"],
            arrowcolor=THEME["text"],
        )
        st.map(
            "Dark.TCombobox",
            fieldbackground=[("readonly", "#1a2233")],
            foreground=[("readonly", THEME["text"])],
        )
        st.configure("TNotebook", background=bg, borderwidth=0, tabmargins=[2, 6, 2, 0])
        st.configure(
            "TNotebook.Tab",
            background=panel,
            foreground=THEME["muted"],
            padding=(16, 8),
            font=("Segoe UI", 10, "bold"),
        )
        st.map(
            "TNotebook.Tab",
            background=[("selected", THEME["panel2"])],
            foreground=[("selected", THEME["text"])],
        )

    @staticmethod
    def _section(parent: tk.Misc, title: str) -> tuple[tk.Frame, tk.Frame]:
        """Return (outer panel, inner body) for dark bordered sections."""
        wrap = tk.Frame(
            parent,
            bg=THEME["panel"],
            highlightbackground=THEME["border"],
            highlightthickness=1,
        )
        tk.Label(
            wrap,
            text=title,
            font=("Segoe UI", 10, "bold"),
            bg=THEME["panel"],
            fg=THEME["muted"],
        ).pack(anchor="w", padx=14, pady=(10, 2))
        body = tk.Frame(wrap, bg=THEME["panel"])
        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 12))
        return wrap, body

    def _build_ui(self) -> None:
        outer = tk.Frame(self, bg=THEME["bg"])
        outer.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        outer.grid_rowconfigure(1, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        header = tk.Frame(
            outer,
            bg=THEME["panel"],
            highlightbackground=THEME["border"],
            highlightthickness=1,
        )
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        tk.Label(
            header,
            text="SIMD vs Scalar — Race Visualizer",
            font=self._title_font,
            bg=THEME["panel"],
            fg=THEME["text"],
        ).pack(anchor="w", padx=14, pady=(12, 0))
        tk.Label(
            header,
            text="Race → run the demo. Results → speedup chart. Learn → why scalar is slower (plain English).",
            font=self._subtitle_font,
            bg=THEME["panel"],
            fg=THEME["muted"],
        ).pack(anchor="w", padx=14, pady=(2, 12))

        self._notebook = ttk.Notebook(outer)
        self._notebook.grid(row=1, column=0, sticky="nsew")

        tab_race = tk.Frame(self._notebook, bg=THEME["bg"])
        tab_results = tk.Frame(self._notebook, bg=THEME["bg"])
        tab_learn = tk.Frame(self._notebook, bg=THEME["bg"])
        self._notebook.add(tab_race, text="  Race  ")
        self._notebook.add(tab_results, text="  Results  ")
        self._notebook.add(tab_learn, text="  Learn  ")

        self._build_race_tab(tab_race)
        self._build_results_tab(tab_results)
        self._build_learn_tab(tab_learn)

    def _build_controls(self, parent: tk.Frame) -> None:
        ctrl_wrap, ctrl = self._section(parent, "Controls")
        ctrl_wrap.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(ctrl, text="Array size:").grid(row=0, column=0, sticky="w")
        size_frame = ttk.Frame(ctrl)
        size_frame.grid(row=0, column=1, padx=6, sticky="w")
        for val, label in ((1_000, "1K"), (10_000, "10K"), (100_000, "100K")):
            ttk.Radiobutton(size_frame, text=label, value=val, variable=self._array_size).pack(
                side=tk.LEFT, padx=4
            )

        ttk.Label(ctrl, text="Operation:").grid(row=0, column=2, padx=(16, 0), sticky="w")
        ttk.Combobox(
            ctrl,
            textvariable=self._operation,
            values=list(OP_LABEL_TO_KEY.keys()),
            state="readonly",
            width=16,
            style="Dark.TCombobox",
        ).grid(row=0, column=3, padx=6, sticky="w")

        ttk.Label(ctrl, text="SIMD width:").grid(row=0, column=4, padx=(16, 0), sticky="w")
        w_frame = ttk.Frame(ctrl)
        w_frame.grid(row=0, column=5, padx=6, sticky="w")
        ttk.Radiobutton(w_frame, text="SSE (4-wide)", value=4, variable=self._simd_width).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Radiobutton(w_frame, text="AVX (8-wide)", value=8, variable=self._simd_width).pack(
            side=tk.LEFT, padx=4
        )

        ttk.Checkbutton(ctrl, text="Sounds", variable=self._sounds).grid(row=0, column=6, padx=(14, 0))
        ttk.Checkbutton(ctrl, text="Step mode", variable=self._step_mode).grid(row=0, column=7, padx=(8, 0))

        btn_frame = ttk.Frame(ctrl)
        btn_frame.grid(row=0, column=8, padx=(16, 0), sticky="e")
        ttk.Button(btn_frame, text="Run Race", style="Accent.TButton", command=self.start_race).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(btn_frame, text="Step +1", command=self.step_once).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Reset", command=self.reset_race).pack(side=tk.LEFT, padx=4)

    def _build_race_tab(self, tab: tk.Frame) -> None:
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        top = tk.Frame(tab, bg=THEME["bg"])
        top.grid(row=0, column=0, sticky="ew", padx=4, pady=4)
        self._build_controls(top)

        race_wrap, race = self._section(tab, "Live race")
        race_wrap.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 4))

        info = tk.Frame(race, bg=THEME["panel2"], highlightbackground=THEME["border"], highlightthickness=1)
        info.pack(fill=tk.X, pady=(0, 10))
        info_inner = tk.Frame(info, bg=THEME["panel2"])
        info_inner.pack(fill=tk.X, padx=10, pady=8)

        self._cycles_saved_label = tk.Label(
            info_inner,
            text="Cycles saved (model): —",
            font=("Segoe UI", 10),
            bg=THEME["panel2"],
            fg=THEME["accent"],
            anchor="w",
        )
        self._cycles_saved_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self._delta_label = tk.Label(
            info_inner,
            text="Live: press Run Race",
            font=("Segoe UI", 10),
            bg=THEME["panel2"],
            fg=THEME["muted"],
            anchor="e",
        )
        self._delta_label.pack(side=tk.RIGHT)

        tk.Label(
            race,
            text="Element progress (scalar index vs SIMD chunk)",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["panel"],
            fg=THEME["muted"],
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 4))

        grid_wrap = tk.Frame(race, bg="#0b1220", highlightbackground=THEME["border"], highlightthickness=1)
        grid_wrap.pack(fill=tk.X)
        self._grid_canvas = tk.Canvas(grid_wrap, bg="#0b1220", highlightthickness=0, height=168)
        self._grid_canvas.pack(fill=tk.X, padx=2, pady=2)

        tk.Label(
            race,
            text="Racetrack (tick race — SIMD reaches the line in fewer steps)",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["panel"],
            fg=THEME["muted"],
            anchor="w",
        ).pack(fill=tk.X, pady=(12, 4))

        track_wrap = tk.Frame(race, bg="#0b1220", highlightbackground=THEME["border"], highlightthickness=1)
        track_wrap.pack(fill=tk.BOTH, expand=True)
        self._track_canvas = tk.Canvas(track_wrap, bg="#0b1220", highlightthickness=0)
        self._track_canvas.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self._track_canvas.bind("<Configure>", lambda _e: self._redraw_track_if_racing())

        hud_wrap = tk.Frame(race, bg=THEME["panel"])
        hud_wrap.pack(fill=tk.X, pady=(10, 0))
        self._scalar_hud = tk.Label(
            hud_wrap,
            text="Scalar: idle",
            font=self._hud_font,
            bg=THEME["panel"],
            fg=THEME["scalar"],
            anchor="w",
        )
        self._scalar_hud.pack(fill=tk.X)
        self._simd_hud = tk.Label(
            hud_wrap,
            text="SIMD: idle",
            font=self._hud_font,
            bg=THEME["panel"],
            fg=THEME["simd"],
            anchor="w",
        )
        self._simd_hud.pack(fill=tk.X)

        self._tip_label = tk.Label(
            race,
            text="Tip: enable Step mode to advance one frame at a time.",
            font=("Segoe UI", 9),
            bg=THEME["panel"],
            fg=THEME["muted"],
            wraplength=900,
            justify=tk.LEFT,
        )
        self._tip_label.pack(fill=tk.X, pady=(8, 4))

    def _build_results_tab(self, tab: tk.Frame) -> None:
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        body = tk.Frame(tab, bg=THEME["panel"], padx=12, pady=12)
        body.grid(row=0, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)

        self._winner_banner = tk.Label(
            body,
            text="Run a race first — results appear here after the animation.",
            font=("Segoe UI", 14, "bold"),
            bg=THEME["panel"],
            fg=THEME["muted"],
            pady=8,
        )
        self._winner_banner.grid(row=0, column=0, sticky="ew")

        self._speedup_badge = tk.Label(
            body,
            text="",
            font=self._speedup_font,
            bg="#1a1204",
            fg=THEME["accent"],
            pady=20,
        )
        self._speedup_badge.grid(row=1, column=0, sticky="ew", pady=8)

        self._result_label = ttk.Label(
            body,
            text="NumPy benchmark: scalar Python loop vs vectorized expression.",
            wraplength=1000,
            justify=tk.LEFT,
        )
        self._result_label.grid(row=2, column=0, sticky="ew", pady=4)

        chart_frame = tk.Frame(body, bg=THEME["panel2"], highlightbackground=THEME["border"], highlightthickness=1)
        chart_frame.grid(row=3, column=0, sticky="ew", pady=10)
        self._canvas_mpl = FigureCanvasTkAgg(self._results.figure, master=chart_frame)
        wdg = self._canvas_mpl.get_tk_widget()
        wdg.configure(bg=THEME["panel"], height=320)
        wdg.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        export_row = ttk.Frame(body)
        export_row.grid(row=4, column=0, sticky="w", pady=4)
        ttk.Button(export_row, text="Export CSV…", command=self._export_csv).pack(side=tk.LEFT, padx=4)
        ttk.Button(export_row, text="Save chart PNG…", command=self._save_chart_png).pack(side=tk.LEFT, padx=4)
        ttk.Button(export_row, text="Save screenshot…", command=self._save_screenshot).pack(side=tk.LEFT, padx=4)

        tk.Label(
            body,
            text="Where SIMD lives on the CPU (simplified)",
            font=("Segoe UI", 10, "bold"),
            bg=THEME["panel"],
            fg=THEME["muted"],
        ).grid(row=5, column=0, sticky="w", pady=(12, 4))

        self._arch_canvas = tk.Canvas(
            body,
            height=120,
            bg=THEME["panel2"],
            highlightthickness=1,
            highlightbackground=THEME["border"],
        )
        self._arch_canvas.grid(row=6, column=0, sticky="ew")
        self._arch_canvas.bind("<Configure>", lambda _e: ResultsPanel.draw_arch_diagram(self._arch_canvas))
        ResultsPanel.draw_arch_diagram(self._arch_canvas)

    def _build_learn_tab(self, tab: tk.Frame) -> None:
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        wrap = tk.Frame(tab, bg=THEME["panel2"], highlightbackground=THEME["border"], highlightthickness=1)
        wrap.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        tk.Label(
            wrap,
            text="Why scalar is slower than SIMD",
            font=("Segoe UI", 14, "bold"),
            bg=THEME["panel2"],
            fg=THEME["text"],
        ).pack(anchor="w", padx=14, pady=(14, 4))
        tk.Label(
            wrap,
            text="Short explanation tied to what you see in the Race and Results tabs.",
            font=("Segoe UI", 10),
            bg=THEME["panel2"],
            fg=THEME["muted"],
        ).pack(anchor="w", padx=14, pady=(0, 10))

        text_frame = tk.Frame(wrap, bg=THEME["panel2"])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 12))

        sb = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        self._learn_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            bg="#0b1220",
            fg=THEME["text"],
            insertbackground=THEME["text"],
            font=("Segoe UI", 11),
            relief=tk.FLAT,
            padx=16,
            pady=16,
            spacing2=4,
            spacing3=8,
            yscrollcommand=sb.set,
        )
        sb.config(command=self._learn_text.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._learn_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _refresh_learn(self) -> None:
        if not hasattr(self, "_learn_text"):
            return
        text = why_scalar_slower_text(int(self._simd_width.get()), self._op_key())
        self._learn_text.config(state=tk.NORMAL)
        self._learn_text.delete("1.0", tk.END)
        self._learn_text.insert(tk.END, text)
        self._learn_text.config(state=tk.DISABLED)

    def _wire_controller(self) -> None:
        hud = _RaceHud(
            scalar_hud=self._scalar_hud,
            simd_hud=self._simd_hud,
            cycles_saved_label=self._cycles_saved_label,
            delta_label=self._delta_label,
            tip_label=self._tip_label,
            grid_canvas=self._grid_canvas,
            track_canvas=self._track_canvas,
        )
        self._controller = RaceController(
            self,
            array_size=self._array_size,
            operation=self._operation,
            simd_width=self._simd_width,
            sounds=self._sounds,
            step_mode=self._step_mode,
            hud=hud,
            draw_grids=self._draw_grids_cb,
            draw_track=self._draw_track_cb,
            on_race_finish=self._on_race_finish,
        )

    def _op_key(self) -> str:
        return OP_LABEL_TO_KEY.get(self._operation.get(), "add")

    def _draw_grids_cb(
        self,
        scalar_elems: int,
        simd_elems: int,
        n: int,
        width: int,
        _op: str,
        _scalar_frac: float,
        _simd_frac: float,
        flash: int,
    ) -> None:
        self._grid_canvas.delete("all")
        st = RaceFrameState(scalar_elems, simd_elems, 0, 0)
        self._drawer.draw_grids(self._grid_canvas, st, n, width)
        if flash > 0:
            cw = max(200, self._grid_canvas.winfo_width())
            self._grid_canvas.create_text(
                cw - 14,
                16,
                anchor="ne",
                text="SIMD chunk",
                fill=THEME["accent"],
                font=("Segoe UI", 9, "bold"),
            )

    def _draw_track_cb(self, scalar_frac: float, simd_frac: float, width: int) -> None:
        self._last_track = (scalar_frac, simd_frac, width)
        self._drawer.draw_track(self._track_canvas, scalar_frac, simd_frac, width)

    def _redraw_track_if_racing(self) -> None:
        if self._last_track and getattr(self._controller, "_phase", "") == "race":
            s, v, w = self._last_track
            self._drawer.draw_track(self._track_canvas, s, v, w)

    def start_race(self) -> None:
        self._controller.start_race()

    def step_once(self) -> None:
        self._controller.step_once()

    def reset_race(self) -> None:
        self._controller.reset()
        self._results.clear_measurements()
        self._winner_banner.config(
            text="Run a race first — results appear here after the animation.",
            fg=THEME["muted"],
        )
        self._speedup_badge.config(text="", bg="#1a1204")
        self._result_label.config(text="NumPy benchmark: scalar Python loop vs vectorized expression.")
        self._results.figure.axes[0].clear()
        self._canvas_mpl.draw_idle()

    def _on_race_finish(self) -> None:
        self._results.finish_race(
            self,
            n=self._controller.n(),
            op=self._controller.op(),
            width=self._controller.width(),
            result_label=self._result_label,
            winner_banner=self._winner_banner,
            speedup_badge=self._speedup_badge,
            canvas_mpl=self._canvas_mpl,
            scroll_canvas=None,
        )
        self._notebook.select(1)

    def _export_csv(self) -> None:
        if not self._results.has_measurements:
            return
        export_csv(
            self,
            n=self._controller.n(),
            op=self._controller.op(),
            width=self._controller.width(),
            t_scalar=self._results.measured_scalar or 0.0,
            t_vector=self._results.measured_vector or 0.0,
        )

    def _save_chart_png(self) -> None:
        save_chart_png(self, self._results.figure)

    def _save_screenshot(self) -> None:
        save_window_screenshot(self)

    def _on_close(self) -> None:
        self._controller.cancel_after()
        self.destroy()
