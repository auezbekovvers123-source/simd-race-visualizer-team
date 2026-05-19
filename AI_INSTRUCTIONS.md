# Instructions for AI assistants (ChatGPT, Copilot, Claude, Cursor, etc.)

Use this file when a teammate works with **any AI** on this repo. Copy the **relevant section** into the AI chat so it follows team rules.

**Repo:** https://github.com/auezbekovvers123-source/simd-race-visualizer-team  
**Run:** `pip install -r requirements.txt` then `python main.py`  
**Platform:** Windows desktop — Python 3.10+, Tkinter (stdlib), NumPy, Matplotlib.

---

## Rules every AI must follow

1. **Only edit your assigned folder** (`person2/` … `person6/`). Do **not** change `person1/` or another teammate’s folder unless Person 1 asks you to integrate after a merge.
2. **Do not delete** other folders or rewrite the whole repo into one file.
3. **Imports:** use package style, e.g. `from person2.race_model import RaceAnimation`, `from person1.config import THEME, OP_LABEL_TO_KEY`.
4. **Keep modules testable:** Person 2 and 3 should avoid importing Tkinter in their core logic.
5. **Match existing style:** type hints, docstrings on public classes, `THEME` colors from `person1.config` for any UI you add.
6. **Git:** work on a branch `personN/short-name`, make **2–4 small commits**, open a PR to `main`. Commit messages: `feat(personN): ...` or `fix(personN): ...`.
7. **Reference implementation:** the course prototype is the single-file app in the older repo `simd-scalar-race-visualizer` (same author). You may **port ideas**, not copy the entire file into one person’s folder.

---

## Project goal (full app)

Build a **SIMD vs Scalar Race Visualizer**:

- **Left:** scalar — one array element active per step.
- **Right:** SIMD — 4-wide (SSE) or 8-wide (AVX) elements active per chunk.
- **Animation:** race finishes with SIMD ahead; live timers / cycle counters.
- **Controls:** array size 1K / 10K / 100K; operations Vector Add, Dot Product, Array Multiply; SSE vs AVX width; Run Race, Reset, optional Step mode.
- **After race:** real NumPy timing (Python loop vs vectorized), speedup text, bar chart.
- **Education:** text explaining SIMD, SSE/AVX, pseudocode for scalar vs SIMD.
- **Stretch:** CSV export, chart PNG, window screenshot, simple CPU architecture diagram.

Person 1 owns integration in `person1/app_shell.py` after your module exists.

---

## Copy-paste prompt — Person 2 (race model)

```text
I am Person 2 on the team repo simd-race-visualizer-team.

Read AI_INSTRUCTIONS.md and only edit person2/.

Create person2/race_model.py with:
- OperationKey type alias (str: "add" | "mul" | "dot")
- ceil_div, logical_scalar_cycles, logical_simd_cycles
- @dataclass RaceFrameState (scalar_elems, simd_elems, scalar_cycles, simd_cycles)
- class RaceAnimation(anim_frames) with method progress(frame, n, width, op) -> RaceFrameState
- method cycles_saved(state) -> int

No Tkinter. Add person2/README.md notes. Use type hints and docstrings.
Do not modify other personN folders.
```

**Files:** `person2/race_model.py`, update `person2/README.md`

---

## Copy-paste prompt — Person 3 (benchmarks)

```text
I am Person 3 on the team repo simd-race-visualizer-team.

Read AI_INSTRUCTIONS.md and only edit person3/.

Create person3/benchmark.py with:
- class BenchmarkEngine with run(n, op) -> tuple[float, float]  # scalar_seconds, vector_seconds
- Operations: add, mul, dot using NumPy
- Pure Python loops for "scalar"; np.add/np.multiply/np.dot (or equivalent) for vectorized
- _pick_repeats(n, scalar) helper so benchmarks finish in reasonable time on 100K

No Tkinter. Add tests or a small __main__ demo optional.
Do not modify other personN folders.
```

**Files:** `person3/benchmark.py`, update `person3/README.md`

---

## Copy-paste prompt — Person 4 (race canvas)

```text
I am Person 4 on the team repo simd-race-visualizer-team.

Read AI_INSTRUCTIONS.md and only edit person4/.

Create person4/race_canvas.py with a class RaceCanvasDrawer (or similar) that:
- Draws scalar grid (one highlighted cell) and SIMD grid (width parallel rows, chunk highlighted)
- Draws dual racetrack with two cars, progress fractions 0..1
- Uses colors from person1.config.THEME
- Methods like draw_grids(canvas, ...) and draw_track(canvas, scalar_frac, simd_frac, width)

Depends on person2.RaceFrameState for indices/progress. Tkinter Canvas only in this file.
Do not modify other personN folders.
```

**Files:** `person4/race_canvas.py`, update `person4/README.md`

---

## Copy-paste prompt — Person 5 (controls & race loop)

```text
I am Person 5 on the team repo simd-race-visualizer-team.

Read AI_INSTRUCTIONS.md and only edit person5/.

Create person5/race_controller.py that:
- Exposes a RaceController or mixin methods for SimdScalarRaceApp
- Wires: array size 1K/10K/100K, operation combobox, SSE(4)/AVX(8), Run Race, Reset, Step mode
- Uses person2.RaceAnimation for frame state each tick
- Calls person4.RaceCanvasDrawer to redraw
- Optional: countdown overlay, winsound beeps on Windows
- HUD labels: wall time ms, logical cycles, elements processed

May import person1.config. Coordinate with app_shell integration via clear public methods.
Do not modify other personN folders.
```

**Files:** `person5/race_controller.py`, update `person5/README.md`

---

## Copy-paste prompt — Person 6 (results & exports)

```text
I am Person 6 on the team repo simd-race-visualizer-team.

Read AI_INSTRUCTIONS.md and only edit person6/.

Create:
- person6/education.py — education_text(width, isa), pseudocode_scalar(op), pseudocode_simd(op, width)
- person6/results.py — matplotlib bar chart, speedup label, finish_race hook using person3.BenchmarkEngine
- person6/export.py — export_csv, save_chart_png, save_screenshot (Windows BMP via ctypes ok)

Use person1.config.THEME for matplotlib dark style if needed.
Do not modify other personN folders.
```

**Files:** `person6/education.py`, `person6/results.py`, `person6/export.py`, update `person6/README.md`

---

## Copy-paste prompt — Person 1 (integration only)

```text
I am Person 1 (repo owner) on simd-race-visualizer-team.

Read AI_INSTRUCTIONS.md. I may edit person1/, main.py, README.md, TEAM.md.

Integrate merged modules into person1/app_shell.py:
- Import RaceAnimation, BenchmarkEngine, RaceCanvasDrawer, RaceController, results/export
- Build full UI: header, controls, race board, scrollable results section
- Keep main.py as thin entry point

Do not remove person2–person6 folders. Preserve git history; small integration commits only.
```

---

## Suggested merge order

```text
main (Person 1 skeleton)
  → merge person2/race-model
  → merge person3/benchmark     # can be parallel with person2
  → merge person4/race-canvas
  → merge person5/race-controller
  → merge person6/results
  → Person 1: integration PR wiring everything in app_shell.py
```

---

## Checklist before opening a PR

- [ ] `python main.py` still runs (or your module imports without error)
- [ ] Only your `personN/` folder changed (+ your branch)
- [ ] `personN/README.md` describes what you built
- [ ] 2+ commits with clear messages
- [ ] PR title: `[Person N] Short description`

---

## If the AI breaks the repo

```powershell
git checkout main
git pull
git checkout -b personN/fix-attempt
# fix only your folder
git add personN/
git commit -m "fix(personN): describe fix"
git push -u origin personN/fix-attempt
```

---

## Questions?

Update **TEAM.md** with real GitHub @handles. Person 1 merges PRs and resolves import conflicts in `app_shell.py`.
