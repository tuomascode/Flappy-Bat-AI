from __future__ import annotations

import pygame

_PANEL_COLOUR = (15, 15, 15, 170)
_LABEL_COLOUR = (160, 160, 160)
_VALUE_COLOUR = (255, 255, 255)
_BEST_COLOUR = (255, 210, 50)

_PANEL_X = 12
_PANEL_Y = 12
_PANEL_W = 230
_ROW_H = 28
_PADDING_X = 16
_VALUE_X = 130


def _draw_frame(
    screen: pygame.Surface,
    towers: list,
    bats: list,
    best_score: float,
    generation: int,
    score: int,
) -> None:
    screen.fill((100, 100, 100))

    for tower in towers:
        pygame.draw.rect(
            screen, (0, 0, 0), tower.get_upper_boarder_sizepos(), border_radius=10
        )
        pygame.draw.rect(
            screen, (0, 0, 0), tower.get_lower_boarder_sizepos(), border_radius=10
        )
        pygame.draw.rect(
            screen, tower.get_color(), tower.get_lower_sizepos(), border_radius=10
        )
        pygame.draw.rect(
            screen, tower.get_color(), tower.get_upper_sizepos(), border_radius=10
        )

    for bat in bats:
        bat._load_images()
        screen.blit(bat.bat1, (bat.x, bat.y))

    rows: list[tuple[str, str, tuple[int, int, int]]] = [
        ("Generation", str(generation), _VALUE_COLOUR),
        ("Score", str(score), _VALUE_COLOUR),
        ("Best score", f"{best_score:.2f}", _BEST_COLOUR),
        ("Bats alive", str(len(bats)), _VALUE_COLOUR),
        ("Gap size", f"{towers[0].hole_between_towers} px", _VALUE_COLOUR),
    ]

    panel_h = _ROW_H * len(rows) + _PADDING_X
    panel = pygame.Surface((_PANEL_W, panel_h), pygame.SRCALPHA)
    panel.fill(_PANEL_COLOUR)
    screen.blit(panel, (_PANEL_X, _PANEL_Y))

    font_label = pygame.font.SysFont("Arial", 15)
    font_value = pygame.font.SysFont("Arial", 18, bold=True)

    for idx, (label, value, colour) in enumerate(rows):
        y = _PANEL_Y + idx * _ROW_H + _PADDING_X // 2
        screen.blit(font_label.render(label, True, _LABEL_COLOUR), (_PANEL_X + _PADDING_X, y + 3))
        screen.blit(font_value.render(value, True, colour), (_PANEL_X + _VALUE_X, y))
