# AI Usage Disclosure — SIMD vs Scalar Race Visualizer

This document describes how **AI assistants** (primarily **Cursor Agent**) were used to design, implement, and evolve this project. It is based on the development sessions that produced the original prototype and the later team repository structure.

**Related repos:**
- **Team project:** https://github.com/auezbekovvers123-source/simd-race-visualizer-team
- **Original prototype:** https://github.com/auezbekovvers123-source/simd-scalar-race-visualizer

---

## 1. AI tools used

| Tool | Role |
|------|------|
| **Cursor Agent** | Main coding assistant: architecture, implementation, refactors, fixes, docs |
| **Cursor Ask mode** | Planning, explanations, folder layout, Git workflow guidance (no automatic edits) |
| **Other AIs (optional)** | Teammates may use ChatGPT, Copilot, Claude, etc. per [AI_INSTRUCTIONS.md](AI_INSTRUCTIONS.md) |

---

## 2. Project timeline (what AI helped build)

### Phase A — Initial prototype (single-file app)

**Human input:** A detailed written specification for a Windows desktop teaching tool:
- Animated scalar vs SIMD “race” (1 element vs 4/8 parallel lanes)
- Controls: array size 1K/10K/100K, operations (Vector Add, Dot Product, Array Multiply), SSE (4) / AVX (8)
- Live timers and logical cycle counters
- NumPy benchmarks: pure Python loop vs vectorized code, speedup multiplier, bar chart
- Education panel: SIMD/SSE/AVX explanation + pseudocode
- Stretch: CSV export, chart PNG, window screenshot, CPU architecture diagram
- Tech: Python, Tkinter, `pip install numpy matplotlib`, one well-commented `.py` file

**AI contribution:**
- Chose **Tkinter + NumPy + Matplotlib** (no browser, no PyQt dependency)
- Generated the full first version of `simd_scalar_race_visualizer.py` (~1300+ lines)
- Implemented animation timeline math (`logical_scalar_cycles`, `logical_simd_cycles`)
- Implemented benchmark helpers with adaptive repeat counts for large N
- Wired GUI: controls, canvas lanes, education text, matplotlib chart, export buttons
- Added Windows screenshot via `ctypes` + GDI (`BitBlt`, BMP output)

**Human role:** Provided requirements, ran the app locally, requested save location (`C:\Users\auyez\simd_scalar_race_visualizer`).

---

### Phase B — Polish and “make it more interesting”

**Human input:** “Make it more interesting / entertaining / better looking / understandable / exciting.”

**AI contribution:**
- **Dark telemetry theme** (panel colors, accent button, matplotlib dark rcParams)
- **Countdown** before race: 3 → 2 → 1 → GO with optional `winsound` beeps
- **Dual racetrack** with two “cars” tied to progress fractions
- **Live delta label** (“SIMD is ahead by X elements”)
- **SIMD chunk flash** and **scalar hot-cell** colors for clearer motion
- **Winner banner** and large **SPEEDUP** badge after benchmarks
- **Step mode** and rotating **race tips**
- **Scrollable results** section so chart/badge stay reachable
- Improved education text (TL;DR analogy, tagged headings in the text panel)

---

### Phase C — Bug fixes and credibility improvements

**Human input:** Implicit from testing (layout overlap, benchmark clarity).

**AI contribution:**
- **Split canvases:** `_grid_canvas` (memory grids) vs `_track_canvas` (racetrack) to fix overlap
- Clarified racetrack uses **tick-based** progress (separate from element grids)
- Benchmark wording: scalar = Python loop, vectorized = NumPy expression-style
- Human-readable operation labels in combobox (`Vector Add`, etc.)
- Screenshot capture simplified (BitBlt-only path, safer ctypes struct writes)
- Architecture diagram redraw only on its canvas `<Configure>`, not whole window

---

### Phase D — Code structure refactor

**AI contribution (same prototype file):**
- Extracted **`RaceAnimation`** + **`RaceFrameState`** (animation model, no Tk)
- Extracted **`BenchmarkEngine`** (timing, no Tk)
- Kept **`SimdScalarRaceApp`** as the Tk composer
- Added module docstrings and type hints for teaching/review

This refactor later became the blueprint for **person2/** and **person3/** in the team repo.

---

### Phase E — Publishing and documentation

**AI contribution:**
- `README.md`, `requirements.txt`, `.gitignore` for the standalone repo
- GitHub repository setup instructions
- Run commands and feature list for graders

---

### Phase F — Team repository (six folders)

**Human input:** Split project for six teammates with visible GitHub contributions; one folder per person.

**AI contribution:**
- Designed folder layout: `person1/` … `person6/`
- Scaffolded Person 1 shell (`config.py`, `app_shell.py`, `main.py`)
- Wrote **[AI_INSTRUCTIONS.md](AI_INSTRUCTIONS.md)** — copy-paste prompts per person for any AI
- Ported **person2** `race_model.py` from prototype `RaceAnimation`
- Ported **person5** `race_controller.py` from prototype race loop (countdown, HUD, sounds)
- Team docs: `TEAM.md`, per-folder `README.md`

**Human role:** Repo owner, collaborator invites, merging pull requests, assigning GitHub usernames in `TEAM.md`.

---

## 3. Example prompts (representative)

These are paraphrased from actual sessions; they show *how* the team directed the AI.

### Initial build
```text
Build a SIMD vs Scalar Race Visualizer desktop app for Windows using Python (Tkinter or PyQt5) with:
- Side-by-side animated scalar vs SIMD race, SSE 4-wide / AVX 8-wide
- Array size 1K/10K/100K, operations Vector Add / Dot Product / Array Multiply
- Run Race and Reset, live cycle counters
- NumPy measured scalar vs vectorized times, speedup, bar chart
- Education panel with SIMD/SSE/AVX explanation and pseudocode
- Single .py file; stretch: CSV, screenshot, CPU diagram
```

### UX upgrade
```text
Can we make it more interesting, more entertaining, better looking, understandable, exciting?
```

### Save location
```text
Save this in folder [simd_scalar_race_visualizer]
```

### Team structure
```text
Divide the project into 6 parts, person1–person6 folders, so everyone has their own area on GitHub.
```

---

## 4. What students should verify manually (human responsibility)

AI-generated code should always be **reviewed and tested** before submission:

| Area | What to check |
|------|----------------|
| **Correctness** | App runs: `pip install -r requirements.txt` → `python main.py` |
| **Pedagogy** | Animation is a *model*; benchmark numbers are *measured* — explain both in the report |
| **Performance** | 100K scalar benchmark may be slow; repeat counts are tuned for demo time |
| **Platform** | Built for Windows (Tkinter, optional `winsound`, GDI screenshot) |
| **Academic honesty** | Each teammate understands their folder; can explain their module in defense |
| **Attribution** | This file + per-person README; Git commits match real authors |

---

## 5. Division of work: human vs AI (summary)

| Task | Primary |
|------|---------|
| Course requirements & grading goals | Human (team) |
| Feature specification | Human |
| Architecture choice (Tkinter, modular split) | AI proposed, human approved |
| Core implementation (prototype) | AI generated, human tested |
| Visual/UX iterations | AI implemented from human feedback |
| Team folder structure & integration plan | AI scaffolded, human assigned owners |
| Individual module code (person2–person6) | AI-assisted per teammate prompts; human commits |
| Final presentation / defense narrative | Human (use prompts in section 6 below) |

---

## 6. Per-module AI assistance (team repo)

| Folder | Module | Typical AI-assisted tasks |
|--------|--------|---------------------------|
| **person1/** | Integration shell | Repo init, `config.py`, `app_shell.py`, `main.py`, docs |
| **person2/** | `race_model.py` | Port `RaceAnimation`, cycle math, dataclasses |
| **person3/** | `benchmark.py` | NumPy timing, `_pick_repeats`, add/mul/dot |
| **person4/** | `race_canvas.py` | Tkinter grids, racetrack, car drawing |
| **person5/** | `race_controller.py` | Countdown, tick loop, HUD, step mode, sounds |
| **person6/** | results / export / education | Charts, CSV/PNG, CPU diagram, pseudocode text |

See [AI_INSTRUCTIONS.md](AI_INSTRUCTIONS.md) for the exact copy-paste blocks given to teammates.

---

## 7. Limitations of AI-generated code

- Animation **logical cycles** are a teaching simplification, not hardware PMU counters.
- NumPy “vectorized” path relies on optimized C/BLAS — not hand-written SSE/AVX intrinsics in Python.
- Full end-to-end integration on team `main` depends on all PRs being merged.
- AI may over-explain or under-test edge cases; **manual QA** before demo day is required.

---

## 8. Declaration (template for report cover page)

> We used AI coding assistants (Cursor Agent and optionally other tools listed in AI_INSTRUCTIONS.md) to accelerate implementation of the SIMD vs Scalar Race Visualizer. All specifications, testing, Git collaboration, and final presentation were directed by the team. Each member is responsible for understanding and being able to explain the code in their assigned folder.

---

## 9. References

- [README.md](README.md) — how to run the team project  
- [TEAM.md](TEAM.md) — members and folders  
- [AI_INSTRUCTIONS.md](AI_INSTRUCTIONS.md) — rules for teammates using other AIs  
- Original prototype: `simd_scalar_race_visualizer/simd_scalar_race_visualizer.py`

*Last updated: May 2026 — reflects development through Person 5 (`race_controller`) and open PRs for Person 4.*
