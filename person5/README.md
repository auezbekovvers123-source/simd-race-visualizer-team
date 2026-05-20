# Person 5 — Controls & race loop

**Owner:** @zhanassylzhakyp-debug

**Files:** `race_controller.py`

- `RaceController` — countdown (3…2…1…GO), continuous tick loop, step mode
- HUD updates (wall time, logical cycles, elements, cycles saved, live delta)
- Optional Windows race sounds via `winsound`
- Uses `person2.RaceAnimation`; drawing via callbacks (wired with person4 by Person 1)

**Integration:** Person 1 connects `RaceController` to the app shell with person4 draw functions.
