import pygame


class Camera:
    def __init__(self, screen_size: pygame.Vector2):
        self.rect = pygame.FRect(0, 0, screen_size.x / 2, screen_size.y / 2)
        self.display_surface = pygame.Surface(self.rect.size)
        self.position = pygame.Vector2(0, 0)
        self.screen = pygame.display.get_surface()

    def clear(self, color="black"):
        self.display_surface.fill(color)

    def draw(self, surfs: list[tuple[pygame.Surface, pygame.Vector2]], on_screen=False):
        if on_screen:
            self.screen.blits(surfs)
        else:
            self.display_surface.blits(surfs)

    def display_on_screen(self):
        self.screen.blit(pygame.transform.scale_by(self.display_surface, 2), self.position)
