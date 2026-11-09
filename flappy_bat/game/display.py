from __future__ import annotations

import pygame

_PANEL_COLOUR = (15, 15, 15, 170)
_LABEL_COLOUR = (160, 160, 160)
_VALUE_COLOUR = (255, 255, 255)
_BEST_COLOUR = (255, 210, 50)

_PANEL_MARGIN = 12
_PANEL_Y = 12
_PANEL_W = 230
_ROW_H = 28
_PADDING_X = 16
_VALUE_X = 130

_ARROW_X = 45
_ARROW_MAX_LEN = 70
_ARROW_MIN_LEN = 14
_ARROW_HEAD = 12
_ARROW_SHAFT_W = 6
_ARROW_DOT_R = 5
_ARROW_THRESHOLD = 0.025
_UP_COLOUR = (80, 190, 230)
_DOWN_COLOUR = (220, 110, 60)
_NEUTRAL_COLOUR = (180, 180, 180)

_TEXT = "text"
_END_HEADER_COLOUR = (200, 200, 255)
_WIN_TEXT_COLOUR = (255, 215, 0)
_WIN_BACKING_COLOUR = (0, 0, 0, 160)

# ---------------------------------------------------------------------------
# Font + surface cache — populated once on the first _draw_frame call.
# All helpers below assume _ensure_fonts() has already been called.
# ---------------------------------------------------------------------------

_f_label: pygame.font.Font | None = None
_f_value: pygame.font.Font | None = None
_f_tower: pygame.font.Font | None = None
_f_header: pygame.font.Font | None = None
_f_win: pygame.font.Font | None = None

# Pre-rendered surfaces for text that never changes
_end_header_surf: pygame.Surface | None = None
_win_overlay_surf: pygame.Surface | None = None  # backing + "YOU WIN" composited

# Pre-filled panel backing surfaces (always the same size)
_main_panel_surf: pygame.Surface | None = None
_end_panel_surf: pygame.Surface | None = None

# Per-string label cache: text → rendered Surface (colour always _LABEL_COLOUR)
_label_surf_cache: dict[str, pygame.Surface] = {}

# End-panel value cache: tuple(rows) → list of rendered value Surfaces
# Re-rendered only when stats change (once per round, not once per frame).
_end_value_cache: dict[tuple, list[pygame.Surface]] = {}


def _ensure_fonts() -> None:
    global _f_label, _f_value, _f_tower, _f_header, _f_win
    global _end_header_surf, _win_overlay_surf
    global _main_panel_surf, _end_panel_surf

    if _f_label is not None:
        return

    _f_label  = pygame.font.SysFont("Arial", 15)
    _f_value  = pygame.font.SysFont("Arial", 18, bold=True)
    _f_tower  = pygame.font.SysFont("Arial", 20, bold=True)
    _f_header = pygame.font.SysFont("Arial", 14, bold=True)
    _f_win    = pygame.font.SysFont("Arial", 80, bold=True)

    _end_header_surf = _f_header.render("Last round", True, _END_HEADER_COLOUR)

    win_text = _f_win.render("YOU WIN", True, _WIN_TEXT_COLOUR)
    pad = 20
    _win_overlay_surf = pygame.Surface(
        (win_text.get_width() + pad * 2, win_text.get_height() + pad * 2), pygame.SRCALPHA
    )
    _win_overlay_surf.fill(_WIN_BACKING_COLOUR)
    _win_overlay_surf.blit(win_text, (pad, pad))

    _main_panel_surf = pygame.Surface((_PANEL_W, _ROW_H * 5 + _PADDING_X), pygame.SRCALPHA)
    _main_panel_surf.fill(_PANEL_COLOUR)

    _end_panel_surf = pygame.Surface((_PANEL_W, _ROW_H * 7 + _PADDING_X), pygame.SRCALPHA)
    _end_panel_surf.fill(_PANEL_COLOUR)


def _label_surf(text: str) -> pygame.Surface:
    if text not in _label_surf_cache:
        assert _f_label is not None
        _label_surf_cache[text] = _f_label.render(text, True, _LABEL_COLOUR)
    return _label_surf_cache[text]


def _end_value_surfs(rows: list[tuple[str, str]]) -> list[pygame.Surface]:
    key = tuple(rows)
    if key not in _end_value_cache:
        assert _f_value is not None
        _end_value_cache[key] = [
            _f_value.render(val, True, _VALUE_COLOUR) for _, val in rows
        ]
    return _end_value_cache[key]


def _draw_win_overlay(screen: pygame.Surface) -> None:
    assert _win_overlay_surf is not None
    x = (screen.get_width()  - _win_overlay_surf.get_width())  // 2
    y = (screen.get_height() - _win_overlay_surf.get_height()) // 2
    screen.blit(_win_overlay_surf, (x, y))



def _draw_end_panel(screen: pygame.Surface, rows: list[tuple[str, str]]) -> None:
    assert _end_panel_surf is not None
    assert _end_header_surf is not None

    panel_x = screen.get_width() - _PANEL_W - _PANEL_MARGIN
    panel_y = screen.get_height() - _end_panel_surf.get_height() - _PANEL_MARGIN

    screen.blit(_end_panel_surf, (panel_x, panel_y))
    screen.blit(_end_header_surf, (panel_x + _PADDING_X, panel_y + _PADDING_X // 2 + 3))

    value_surfs = _end_value_surfs(rows)
    for idx, (label, _) in enumerate(rows):
        y = panel_y + (idx + 1) * _ROW_H + _PADDING_X // 2
        screen.blit(_label_surf(label), (panel_x + _PADDING_X, y + 3))
        screen.blit(value_surfs[idx], (panel_x + _VALUE_X, y))


def _draw_output_arrow(screen: pygame.Surface, featured_bat: object) -> None:
    h = screen.get_height()

    output: float = getattr(featured_bat, "last_output", 0.0)
    bat_y: float  = getattr(featured_bat, "y", 0.0)
    bat_h: float  = getattr(featured_bat, "height", 0.0)
    mid_y = int(bat_y + bat_h / 2)
    mid_y = max(_ARROW_HEAD + _ARROW_MAX_LEN, min(h - _ARROW_HEAD - _ARROW_MAX_LEN, mid_y))

    if abs(output) < _ARROW_THRESHOLD:
        pygame.draw.circle(screen, _NEUTRAL_COLOUR, (_ARROW_X, mid_y), _ARROW_DOT_R)
        return

    shaft  = int(_ARROW_MIN_LEN + (_ARROW_MAX_LEN - _ARROW_MIN_LEN) * min(1.0, abs(output)))
    colour = _UP_COLOUR if output < 0 else _DOWN_COLOUR

    pygame.draw.circle(screen, colour, (_ARROW_X, mid_y), _ARROW_DOT_R)

    if output < 0:
        shaft_top = mid_y - shaft
        tip_y     = shaft_top - _ARROW_HEAD
        pygame.draw.rect(screen, colour,
                         (_ARROW_X - _ARROW_SHAFT_W // 2, tip_y + _ARROW_HEAD, _ARROW_SHAFT_W, shaft))
        pygame.draw.polygon(screen, colour, [
            (_ARROW_X - _ARROW_HEAD, shaft_top),
            (_ARROW_X + _ARROW_HEAD, shaft_top),
            (_ARROW_X, tip_y),
        ])
    else:
        shaft_bottom = mid_y + shaft
        tip_y        = shaft_bottom + _ARROW_HEAD
        pygame.draw.rect(screen, colour,
                         (_ARROW_X - _ARROW_SHAFT_W // 2, mid_y, _ARROW_SHAFT_W, shaft))
        pygame.draw.polygon(screen, colour, [
            (_ARROW_X - _ARROW_HEAD, shaft_bottom),
            (_ARROW_X + _ARROW_HEAD, shaft_bottom),
            (_ARROW_X, tip_y),
        ])


def _draw_frame(
    screen: pygame.Surface,
    towers: list,
    bats: list,
    best_score: float,
    generation: int,
    score: int,
    featured_bat: object | None = None,
    end_stats: list[tuple[str, str]] | None = None,
    win: bool = False,
) -> None:
    _ensure_fonts()
    assert _f_tower is not None
    assert _f_value is not None
    assert _main_panel_surf is not None

    screen.fill((100, 100, 100))

    for idx, tower in enumerate(towers):
        pygame.draw.rect(screen, (0, 0, 0), tower.get_upper_boarder_sizepos(), border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), tower.get_lower_boarder_sizepos(), border_radius=10)
        pygame.draw.rect(screen, tower.get_color(), tower.get_lower_sizepos(), border_radius=10)
        pygame.draw.rect(screen, tower.get_color(), tower.get_upper_sizepos(), border_radius=10)
        pos, size = tower.get_lower_sizepos()
        label = _f_tower.render(str(score + 1 + idx), True, (255, 255, 255))
        screen.blit(label, (pos[0] + (size[0] - label.get_width()) // 2, pos[1] + 8))

    for bat in bats:
        bat._load_images()
        screen.blit(bat.bat1, (bat.x, bat.y))

    if featured_bat is not None:
        _draw_output_arrow(screen, featured_bat)

    rows: list[tuple[str, str, str, tuple[int, int, int]]] = [
        (_TEXT, "Generation", str(generation),                        _VALUE_COLOUR),
        (_TEXT, "Score",      str(score),                             _VALUE_COLOUR),
        (_TEXT, "Best score", f"{best_score * 100:.2f}",              _BEST_COLOUR),
        (_TEXT, "Bats alive", str(len(bats)),                         _VALUE_COLOUR),
        (_TEXT, "Gap size",   f"{towers[0].hole_between_towers} px",  _VALUE_COLOUR),
    ]

    panel_x = screen.get_width() - _PANEL_W - _PANEL_MARGIN
    screen.blit(_main_panel_surf, (panel_x, _PANEL_Y))

    for idx, (kind, label, val, colour) in enumerate(rows):
        y = _PANEL_Y + idx * _ROW_H + _PADDING_X // 2
        screen.blit(_label_surf(label), (panel_x + _PADDING_X, y + 3))
        if kind == _TEXT:
            screen.blit(_f_value.render(val, True, colour), (panel_x + _VALUE_X, y))

    if win:
        _draw_win_overlay(screen)
    if end_stats is not None:
        _draw_end_panel(screen, end_stats)
