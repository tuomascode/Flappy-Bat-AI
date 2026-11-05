# Flappy Bat AI — Project Plan

## What This Is

A Flappy Bird clone where only an AI can play. The AI is a custom
topologically-evolving neural network (similar to NEAT). It controls the bat's
*acceleration*, not discrete jumps, which makes the learning task harder.

---

## History

| Date | Work |
|------|------|
| Summer 2022 | Original implementation: game engine, neural network, evolution loop |
| Nov 2026 | Added testing infrastructure; started refactoring plan |

---

## Testing Plan

### Philosophy
Tests should catch regressions during refactoring without requiring a running
game or pygame display. All tests use `pytest`.

### What is covered

**`tests/test_nemt.py`** — pure Python, no display needed
- `Node`: construction, `append_neighbour`, `solve_network_output` (no inputs,
  one input, multiple inputs)
- `Network`: construction shape, connections, `return_network_solution`,
  `calculate_complexicity`, `create_new_node`, `remove_node`,
  `create_new_connection`, `remove_connection`, `mutate_network` (all rates),
  `write`/`read_and_return` roundtrip, `return_mutated_network`
- `Evolution`: `create_new_networks`, `evolve_networks` (with and without
  complexity), `read_and_return`

**`tests/test_towers.py`** — pygame imported but no display needed for Towers
- Construction: hole size clamping, boundary within screen
- Getters: return correct tuple shapes and color
- Movement: `move`, `move_backwards`, `move_half` all update x correctly
- `check_if_tower_passed`: correct before and after threshold

### What is NOT yet covered (requires refactoring first)

- `Bat` — `__init__` calls `pygame.image.load`; needs the image dependency
  extracted before unit testing collision/movement logic is clean
- `run_with_pygame` / `run_without_pygame` — integration tests, need a headless
  mode that doesn't need a real display; blocked by DRY refactor below
- `main()` evolution loop — end-to-end; would use pre-seeded networks

---

## Refactoring Plan

The goal is a clean, readable codebase while keeping the core algorithm
identical: the same NEAT-like topological evolution, the same physics, the same
game rules, the same seeded obstacle course.

Each phase can be validated by running `pytest` before moving on.

---

### Phase 1 — Safe cosmetic fixes (zero behaviour change)

These are mechanical edits with no logic impact. Do them first so the diff for
later phases is easier to read.

| # | What | Where |
|---|------|--------|
| 1.1 | Rename `calculate_complexicity` → `calculate_complexity` everywhere | NEMT.py |
| 1.2 | Rename `variablity` → `variability` everywhere | NEMT.py |
| 1.3 | Add `@staticmethod` to `return_mutated_network` and `read_and_return` | NEMT.py |
| 1.4 | Replace `== False` / `== True` with `not` / bare truthiness | main.py |
| 1.5 | Replace string concatenation in display writes with f-strings | main.py |
| 1.6 | Remove the commented-out `print` on NEMT.py:308 | NEMT.py |
| 1.7 | Remove the uncertain `del deletion_value` lines | main.py |
| 1.8 | Rename Finnish variable `maara` → `count` | NEMT.py |
| 1.9 | Rename Finnish variable `poisto` → `removal` | NEMT.py |
| 1.10 | Rename Finnish variable `apunetwork_list` → `candidate_sources` | NEMT.py |

After Phase 1: all 75 existing tests should still pass unchanged.

---

### Phase 2 — Bug fixes

| # | What | Where |
|---|------|--------|
| 2.1 | Fix bare `except` in `Node.solve_network_output` → `except (TypeError, OverflowError)` | NEMT.py:22 |
| 2.2 | Fix `primitive` flag not restored in `remove_node` — add `if len(self.levels) == 0: self.primitive = True` after clearing levels | NEMT.py:121 |

After Phase 2: update `test_remove_node_clears_levels` to assert `primitive is True`.

---

### Phase 3 — Extract constants

Move all magic numbers to a `constants` block at the top of each file. No
logic change, just named references.

**NEMT.py** constants block:
```python
_WEIGHT_INIT_RANGE  = (-1.0, 1.0)   # initial input→output weights
_BIAS_INIT_RANGE    = (-2.0, 2.0)   # output node bias
_ACCEL_SCALE        = 0.025         # network output → acceleration delta
```

**main.py** constants block:
```python
SCREEN_WIDTH        = 1000
SCREEN_HEIGHT       = 800
TOWER_WIDTH         = 50
TOWER_MOVE_SPEED    = 3
TOWER_SPACING       = 200
TOWER_GAP_MAX       = 325
TOWER_GAP_MIN       = 135
TOWER_BOUNDARY      = 30
ACCEL_SCALE         = 0.025
POPULATION_SIZE     = 500
STAGNATION_LIMIT    = 10
MIN_VIABLE_SCORE    = 8
```

After Phase 3: tests pass; code reads like documentation.

---

### Phase 4 — Structural: DRY up the simulation loop

`run_with_pygame` and `run_without_pygame` share ~90% of logic. The only real
difference is whether the screen is painted each frame.

**Approach:** collapse them into one function:

```python
def run_simulation(bats, best_score, generation, *, display: bool) -> list:
    ...
    while True:
        ...
        if display:
            _draw_frame(screen, towers, bats, best_score, generation, score)
        ...
```

Extract the drawing code into a private `_draw_frame(...)` helper so the main
loop stays readable. The `run_without_pygame` loading screen becomes a one-time
call before the first headless generation.

`main()` then calls `run_simulation(..., display=False)` or
`run_simulation(..., display=True)` depending on whether a viable candidate has
been found.

After Phase 4: add an integration test that runs one headless generation with a
small population (10 bats, seeded) and checks that it returns scored results.

---

### Phase 5 — Decouple `Bat` from pygame

Currently `Bat.__init__` calls `pygame.image.load` unconditionally, making the
class untestable without a display.

**Approach:** lazy-load the images:

```python
class Bat:
    def __init__(self, network):
        self._images_loaded = False
        ...

    def _load_images(self):
        if not self._images_loaded:
            if randint(0, 1) == 1:
                self.bat1 = pygame.image.load("flap1.png")
                self.bat2 = pygame.image.load("flap2.png")
            else:
                self.bat1 = pygame.image.load("flap2.png")
                self.bat2 = pygame.image.load("flap1.png")
            self._images_loaded = True
```

The drawing code in `_draw_frame` calls `bat._load_images()` before blitting.
Headless mode never calls `_load_images`, so no display is needed.

After Phase 5: add tests for `Bat.check_impact` and `Bat.move_bat` by
constructing bats with mock networks and no pygame display.

---

### Phase 6 — Type hints

Add type annotations to all public methods. This is last because the hints
should reflect the final refactored signatures, not the originals.

Minimal target (most valuable for understanding the data flow):
```python
class Network:
    def return_network_solution(self, inputs: list[float]) -> list[float]: ...
    def create_new_node(self, mutability: int = 1) -> None: ...
    def mutate_network(self, rate: int) -> None: ...
    def write(self, filename: str) -> None: ...

class Evolution:
    def create_new_networks(self, input_nodes: int, output_nodes: int, ...) -> list[Network]: ...
    def evolve_networks(self, network: Network, ...) -> list[Network]: ...
```

---

### What does NOT change

- The evolution algorithm logic inside `evolve_networks` and `create_new_networks`
- The network table representation (2-D list, `None` = no connection)
- The recursive `solve_network_output` using `tanh`
- The game physics (acceleration model, collision detection, scoring formula)
- The seeded obstacle course (`seed(1)`)
- The population strategy in `main()` (best + second-best, 4 × N/4)

---

## Backlog

### High priority

- [ ] **DRY up the two `run_*` functions** — `run_with_pygame` and
  `run_without_pygame` share ~90% of code. Extract the shared simulation loop
  into a single function with a `display: bool` parameter.
- [ ] **Decouple `Bat` from pygame** — move `pygame.image.load` out of
  `__init__` so collision/movement logic can be unit tested.
- [ ] **Fix bare `except`** in `Node.solve_network_output` — the silent bare
  except masks bugs; replace with `except (TypeError, OverflowError)`.
- [ ] **Fix `primitive` flag not restored** — `remove_node` empties `levels`
  but never sets `self.primitive = True`; caught by test
  `test_remove_node_clears_levels`.

### Medium priority

- [ ] **Extract magic numbers** — `325`, `135`, `30`, `50`, `0.025`, screen
  dimensions, etc. belong in a config section or constants module.
- [ ] **Fix typo `calculate_complexicity`** → `calculate_complexity`
- [ ] **Fix typo `variablity`** → `variability` throughout NEMT.py
- [ ] **Mark static methods** — `return_mutated_network` and `read_and_return`
  are called without `self`; add `@staticmethod`.
- [ ] **Replace `== False`** comparisons with `not` in `main()`.

### Low priority

- [ ] Remove commented-out `print` on NEMT.py:308
- [ ] Replace manual string concatenation in display text with f-strings
- [ ] Add type hints to public methods
