# Flappy Bat AI — Agent Context & Project Plan

> **For the agent:** Read this file first. It contains everything you need to
> understand the project, the active request, and what must not change. After
> completing a request, clear the **Active Request** section and add a one-line
> entry to **History**.

---

## Project Brief

A Flappy Bird clone where only an AI can play. The AI is a custom
topologically-evolving neural network (similar to NEAT) implemented from
scratch. It controls the bat's *acceleration*, not discrete jumps — a harder
learning task than the standard Flappy Bird formulation.

**Language:** Python 3.11  
**Runtime deps:** `pygame`  
**Dev deps:** `pytest`, `pytest-cov`  
**Venv:** `flappy\` (Windows). Run tests with `.\flappy\Scripts\python.exe -m pytest --cov`

---

## Architecture

```
Flappy-Bat-AI/
  flappy_bat/
    __init__.py
    constants.py          SCREEN_WIDTH, TOWER_*, ACCEL_SCALE, POPULATION_SIZE, …
    network/
      __init__.py         re-exports Node, Network, Evolution
      node.py             Node class
      network.py          Network class
      evolution.py        Evolution class
    game/
      __init__.py
      towers.py           Towers class
      bat.py              Bat class
      simulation.py       run_simulation, _show_loading_screen, main()
      display.py          _draw_frame (separate for future network overlay)
  assets/
    flap1.png
    flap2.png
  tests/
    conftest.py    sets SDL_VIDEODRIVER=dummy, SDL_AUDIODRIVER=dummy
    network/
      test_node.py        Node unit tests (7 tests)
      test_network.py     Network unit tests (31 tests)
      test_evolution.py   Evolution unit tests (9 tests)
    game/
      test_bat.py         Bat unit tests (20 tests)
      test_towers.py      Towers unit tests (27 tests)
  main.py          thin entry point (~4 lines)
  pyproject.toml   pytest + coverage config
```

### Key classes

| Class | File | Responsibility |
|-------|------|----------------|
| `Node` | flappy_bat/network/node.py | Single node; recursive `solve_network_output()` via `tanh` |
| `Network` | flappy_bat/network/network.py | 2-D adjacency table, mutation ops, forward pass |
| `Evolution` | flappy_bat/network/evolution.py | Population factory and evolution strategy |
| `Towers` | flappy_bat/game/towers.py | Obstacle pair; moves left each frame |
| `Bat` | flappy_bat/game/bat.py | Physics object; asks network for acceleration delta |

### Critical invariants (do not break these)

- Network table is a `list[list[float | None]]`; `None` means no connection.
- `solve_network_output()` is recursive with `tanh`; do not replace with iterative.
- Game uses `seed(1)` for the obstacle course; keep this fixed.
- Bat controls **acceleration**, not position or velocity directly.
- Population strategy: best + second-best, 4 × N/4 evolved batches.

---

## Development Philosophy

1. **Test-driven.** New behaviour gets a test before or alongside the
   implementation. Refactors require existing tests to pass unchanged.
2. **Coverage tracked.** Run `.\flappy\Scripts\python.exe -m pytest --cov`
   after every session. The coverage table in this file is kept up to date.
3. **No silent failures.** Bare `except:` is banned. Catch specific exceptions.
4. **No dead code.** Unused attributes, commented-out prints, and dead `main()`
   stubs get deleted.
5. **Constants over magic numbers.** Named constants in a block at the top of
   each file; no inline literals.

## Workflow

Working branch: `vtuomas/opus-refactor`

After every completed phase or feature:
1. Run `.\flappy\Scripts\python.exe -m pytest --cov` — all tests must pass.
2. Stage relevant files (never `git add -A`; name files explicitly).
3. Commit with a short message: `phase N: <one-line summary>`.
4. Update the **Coverage** table and **History** in this file and include
   `project_plan.md` in the same commit.
5. Keep `.gitignore` current — venv (`flappy/`), `__pycache__/`, `.coverage`,
   `.pytest_cache/` must always be excluded.

---

## Coverage

Last measured: **2026-11-05**  
Run: `.\flappy\Scripts\python.exe -m pytest --cov --cov-report=term-missing`
Source: `flappy_bat` package

| File | Stmts | Miss | Cover | Notable uncovered |
|------|-------|------|-------|-------------------|
| flappy_bat/constants.py | 15 | 0 | **100%** | |
| flappy_bat/network/node.py | 22 | 2 | **91%** | `solve_network_output` error branch |
| flappy_bat/network/network.py | 311 | 27 | **91%** | `create_new_networks` complexity paths; mutation branches |
| flappy_bat/network/evolution.py | 65 | 14 | **78%** | `evolve_networks` growth/shrink branches |
| flappy_bat/game/bat.py | 45 | 9 | **80%** | `_load_images` |
| flappy_bat/game/towers.py | 45 | 0 | **100%** | |
| flappy_bat/game/display.py | 17 | 17 | **0%** | `_draw_frame` (display path only) |
| flappy_bat/game/simulation.py | 109 | 109 | **0%** | `run_simulation`; `main()` loop |
| **Total** | **632** | **178** | **72%** | |

The `simulation.py` and `display.py` gaps are expected until the Phase 9 integration test is added.

---

## Planned Work

### Phase 8 — Clean code

Targeted improvements within the new file layout. No algorithm changes.

| # | File | What | Why |
|---|------|------|-----|
| 8.1 | network.py | Rename `create_new_network` → `_rebuild_node_graph` | Name sounds like a constructor; it's a private post-mutation rebuild. |
| 8.2 | network.py | Fix shadow variable in `mutate_network`: `for index, row in enumerate(self.network_table)` | `network_list` is currently used for both the table and each row. |
| 8.3 | network.py | Fix bare `except: continue` in `create_new_node` → `except IndexError` | Same class as the already-fixed bare `except` in `Node`. |
| 8.4 | network.py | Delete dead `main()` at bottom of NEMT.py | References undefined `verkot`; never called. |
| 8.5 | evolution.py | Delete unused `self.mutatibility = 5` from `Evolution.__init__` | Typo-named; never read. |
| 8.6 | evolution.py | Replace apology comment block in `evolve_networks` with accurate docstring | Current comment admits author doesn't understand the code. |
| 8.7 | simulation.py | Replace `best_bat_network = False` sentinel with `None` | `False` is semantically wrong; `None` is idiomatic. |
| 8.8 | simulation.py | Extract stagnation reset block → `_reset_search()` | 7-line state mutation inline; naming it makes the main loop readable. |

**Success criteria:** all tests pass; `evolve_networks` has an accurate
one-paragraph docstring.

---

### Phase 9 — Integration test for `run_simulation`

Add the headless integration test deferred from Phase 4:

```python
def test_headless_simulation_returns_scored_results():
    seed(1)
    nets = Evolution().create_new_networks(5, 1, number_of_networks=10)
    bats = [Bat(n) for n in nets]
    results = run_simulation(bats, 0, 1, display=False)
    assert len(results) == 10
    assert all(isinstance(score, float) for _, score in results)
```

Lives in `tests/game/test_simulation.py`. Runs headless via conftest.py SDL
dummy drivers. Expected to bring `main.py` coverage above 70%.

---

### Feature A — Save and reload best network

Auto-save best network to `checkpoints/best.txt` on each new high score.
Add `--load <path>` CLI argument to resume, skipping viable-candidate search.

**Structural note:** `Network.write` / `Network.read_and_return` already handle
serialisation. This is `argparse` + checkpoint directory plumbing only.

---

### Feature B — Configurable game state

Extract a `GameState` dataclass so arbitrary start positions are reproducible:

```python
@dataclass
class GameState:
    bat_x: int = 60
    bat_y: int = 500
    bat_speed: float = 0.0
    bat_acceleration: float = 0.0
    seed_value: int = 1
    start_score: int = 0
```

`run_simulation` accepts an optional `GameState`. Prerequisite for Feature C.

---

### Feature C — Initial candidate selection via structured tests

Replace the full-game viable-candidate search with a `quick_score(network)` 
function in a new `evaluation.py`. Runs the network against fixed
`GameState` input scenarios (no pygame) and returns a rough fitness estimate.
Pre-filters the initial population before full game evaluation.

**Prerequisite:** Feature B.

---

### Feature D — Network visualisation overlay

Draw the neural network graph alongside the game during the display phase:
nodes as circles, weighted connections as lines, active path highlighted,
acceleration output shown as a direction arrow.

Lives entirely in `display.py`. No game-logic changes required.

---

## Active Request

*None — waiting for next request.*

---

## History

| Date | Action |
|------|--------|
| Summer 2022 | Original implementation: game, neural network, evolution loop |
| 2026-11-05 | Phases 1–6: cosmetic fixes, bug fixes, constants, DRY simulation loop, lazy pygame decoupling, type hints. 95 tests. |
| 2026-11-05 | Restructured project_plan.md as agent context document; added pytest-cov; established coverage baseline (72% total, NEMT 88%, main 44%); created pyproject.toml. |
| 2026-11-05 | Phase 7: Restructured flat layout into `flappy_bat` package (network/, game/); split NEMT.py and main.py; moved assets/; split tests into network/ and game/ subdirs; 95 tests pass. |
