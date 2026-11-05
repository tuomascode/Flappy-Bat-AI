from __future__ import annotations

import pygame


def _draw_frame(screen: pygame.Surface, towers: list, bats: list, best_score: float, generation: int, score: int) -> None:
    screen.fill((100, 100, 100))
    for tower in towers:
        pygame.draw.rect(screen, (0, 0, 0), tower.get_upper_boarder_sizepos(), border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), tower.get_lower_boarder_sizepos(), border_radius=10)
        pygame.draw.rect(screen, tower.get_color(), tower.get_lower_sizepos(), border_radius=10)
        pygame.draw.rect(screen, tower.get_color(), tower.get_upper_sizepos(), border_radius=10)
    for bat in bats:
        bat._load_images()
        screen.blit(bat.bat1, (bat.x, bat.y))
    font = pygame.font.SysFont("Times New Roman", 24)
    text  = font.render(f"{len(bats)} Bats alive. Current Score: {score} Generation: {generation}", True, (255, 255, 255))
    text2 = font.render(f"Best_score: {'%.2f' % best_score} Hole_between_towers: {towers[0].hole_between_towers}", True, (255, 255, 255))
    screen.blit(text,  (25, 25))
    screen.blit(text2, (25, 50))
