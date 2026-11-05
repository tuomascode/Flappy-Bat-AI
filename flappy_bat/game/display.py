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
_REC_COLOUR = (220, 50, 50)
_REC_DOT_R = 6
_REC_X = 14
_REC_Y = 14


def _draw_rec_indicator(screen: pygame.Surface) -> None:
    pygame.draw.circle(screen, _REC_COLOUR, (_REC_X, _REC_Y), _REC_DOT_R)
    font = pygame.font.SysFont("Arial", 15, bold=True)
    screen.blit(font.render("REC", True, _REC_COLOUR), (_REC_X + _REC_DOT_R + 4, _REC_Y - 7))


def _draw_end_panel(
    screen: pygame.Surface,
    rows: list[tuple[str, str]],
) -> None:
    panel_x = screen.get_width() - _PANEL_W - _PANEL_MARGIN
    n_rows = len(rows) + 1
    panel_h = _ROW_H * n_rows + _PADDING_X
    panel_y = screen.get_height() - panel_h - _PANEL_MARGIN

    panel = pygame.Surface((_PANEL_W, panel_h), pygame.SRCALPHA)
    panel.fill(_PANEL_COLOUR)
    screen.blit(panel, (panel_x, panel_y))

    font_header = pygame.font.SysFont("Arial", 14, bold=True)
    font_label = pygame.font.SysFont("Arial", 15)
    font_value = pygame.font.SysFont("Arial", 18, bold=True)

    y = panel_y + _PADDING_X // 2
    screen.blit(font_header.render("Last round", True, _END_HEADER_COLOUR), (panel_x + _PADDING_X, y + 3))

    for idx, (label, val) in enumerate(rows):
        y = panel_y + (idx + 1) * _ROW_H + _PADDING_X // 2
        screen.blit(font_label.render(label, True, _LABEL_COLOUR), (panel_x + _PADDING_X, y + 3))
        screen.blit(font_value.render(val, True, _VALUE_COLOUR), (panel_x + _VALUE_X, y))


def _draw_output_arrow(screen: pygame.Surface, featured_bat: object) -> None:
    h = screen.get_height()

    output: float = getattr(featured_bat, "last_output", 0.0)
    bat_y: float = getattr(featured_bat, "y", 0.0)
    bat_h: float = getattr(featured_bat, "height", 0.0)
    mid_y = int(bat_y + bat_h / 2)
    mid_y = max(_ARROW_HEAD + _ARROW_MAX_LEN, min(h - _ARROW_HEAD - _ARROW_MAX_LEN, mid_y))

    if abs(output) < _ARROW_THRESHOLD:
        pygame.draw.circle(screen, _NEUTRAL_COLOUR, (_ARROW_X, mid_y), _ARROW_DOT_R)
        return

    shaft = int(_ARROW_MIN_LEN + (_ARROW_MAX_LEN - _ARROW_MIN_LEN) * min(1.0, abs(output)))
    colour = _UP_COLOUR if output < 0 else _DOWN_COLOUR

    pygame.draw.circle(screen, colour, (_ARROW_X, mid_y), _ARROW_DOT_R)

    if output < 0:
        shaft_top = mid_y - shaft
        tip_y = shaft_top - _ARROW_HEAD
        pygame.draw.rect(screen, colour,
                         (_ARROW_X - _ARROW_SHAFT_W // 2, tip_y + _ARROW_HEAD, _ARROW_SHAFT_W, shaft))
        pygame.draw.polygon(screen, colour, [
            (_ARROW_X - _ARROW_HEAD, shaft_top),
            (_ARROW_X + _ARROW_HEAD, shaft_top),
            (_ARROW_X, tip_y),
        ])
    else:
        shaft_bottom = mid_y + shaft
        tip_y = shaft_bottom + _ARROW_HEAD
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
    tickrate: int = 0,
    end_stats: list[tuple[str, str]] | None = None,
    recording: bool = False,
) -> None:
    screen.fill((100, 100, 100))

    font_tower = pygame.font.SysFont("Arial", 20, bold=True)
    for idx, tower in enumerate(towers):
        pygame.draw.rect(screen, (0, 0, 0), tower.get_upper_boarder_sizepos(), border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), tower.get_lower_boarder_sizepos(), border_radius=10)
        pygame.draw.rect(screen, tower.get_color(), tower.get_lower_sizepos(), border_radius=10)
        pygame.draw.rect(screen, tower.get_color(), tower.get_upper_sizepos(), border_radius=10)
        pos, size = tower.get_lower_sizepos()
        label = font_tower.render(str(score + 1 + idx), True, (255, 255, 255))
        screen.blit(label, (pos[0] + (size[0] - label.get_width()) // 2, pos[1] + 8))

    for bat in bats:
        bat._load_images()
        screen.blit(bat.bat1, (bat.x, bat.y))

    if featured_bat is not None:
        _draw_output_arrow(screen, featured_bat)

    rows: list[tuple[str, str, str, tuple[int, int, int]]] = [
        (_TEXT, "Generation", str(generation),                        _VALUE_COLOUR),
        (_TEXT, "Score",      str(score),                             _VALUE_COLOUR),
        (_TEXT, "Best score", f"{best_score * 100:.2f}",               _BEST_COLOUR),
        (_TEXT, "Bats alive", str(len(bats)),                         _VALUE_COLOUR),
        (_TEXT, "Gap size",   f"{towers[0].hole_between_towers} px",  _VALUE_COLOUR),
        (_TEXT, "Tickrate",   "uncapped" if tickrate == 0 else f"{tickrate} fps", _VALUE_COLOUR),
    ]

    panel_x = screen.get_width() - _PANEL_W - _PANEL_MARGIN
    panel_h = _ROW_H * len(rows) + _PADDING_X
    panel = pygame.Surface((_PANEL_W, panel_h), pygame.SRCALPHA)
    panel.fill(_PANEL_COLOUR)
    screen.blit(panel, (panel_x, _PANEL_Y))

    font_label = pygame.font.SysFont("Arial", 15)
    font_value = pygame.font.SysFont("Arial", 18, bold=True)

    for idx, (kind, label, val, colour) in enumerate(rows):
        y = _PANEL_Y + idx * _ROW_H + _PADDING_X // 2
        screen.blit(font_label.render(label, True, _LABEL_COLOUR), (panel_x + _PADDING_X, y + 3))
        if kind == _TEXT:
            screen.blit(font_value.render(val, True, colour), (panel_x + _VALUE_X, y))
        else:
            _draw_bar(screen, panel_x + _VALUE_X, y + 4, float(val), colour)

    if end_stats is not None:
        _draw_end_panel(screen, end_stats)
    if recording:
        _draw_rec_indicator(screen)
