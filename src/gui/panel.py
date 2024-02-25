import pygame
from gui.element import UIContainer
from gui.manager import UIManager

class UIPanel(UIContainer):
    def __init__(self, rect: pygame.Rect, manager: UIManager, container : "UIContainer" = None) -> None:
        super().__init__(rect, manager, container)
        self._image = pygame.Surface(rect.size, pygame.SRCALPHA)
        self._image.fill(self._manager.ressources["colors"]["default"])
        self._container_image = self._image.copy()