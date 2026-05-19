"""Main Tk window skeleton — Person 1. Teammates wire modules from person2–person6."""

import tkinter as tk
from tkinter import ttk

from person1.config import THEME


class SimdScalarRaceApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("SIMD vs Scalar Race Visualizer (Team)")
        self.geometry("960x640")
        self.minsize(720, 480)
        self.configure(bg=THEME["bg"])

        header = tk.Frame(
            self,
            bg=THEME["panel"],
            highlightbackground="#243152",
            highlightthickness=1,
        )
        header.pack(fill=tk.X, padx=12, pady=12)

        tk.Label(
            header,
            text="SIMD vs Scalar — Race Visualizer",
            font=("Segoe UI", 16, "bold"),
            bg=THEME["panel"],
            fg=THEME["text"],
        ).pack(anchor="w", padx=14, pady=(12, 4))

        tk.Label(
            header,
            text=(
                "Person 1: app shell loaded. "
                "Teammates implement person2–person6 modules via pull requests."
            ),
            font=("Segoe UI", 10),
            bg=THEME["panel"],
            fg=THEME["muted"],
            wraplength=720,
            justify=tk.LEFT,
        ).pack(anchor="w", padx=14, pady=(0, 12))

        body = ttk.LabelFrame(self, text="Status", padding=12)
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        ttk.Label(
            body,
            text="Run Race, benchmarks, and charts will appear as person2–person6 PRs merge.",
        ).pack(anchor="w")
