import pygame

from gui.element import UIContainer, UIElement
from gui.manager import UIManager

class UIImage(UIElement):
    def __init__(self, rect: pygame.Rect, manager: UIManager, container: UIContainer = None) -> None:
        super().__init__(rect, manager, container)
        self.images = {}
    
    def set_image(self, id : str):
        self._image = self.images[id].copy()
    
    def get_position(self) -> tuple:
        c_pos = super().get_position()
        if self._image:
            s_pos = pygame.Vector2(self.get_size()) * 0.5 - pygame.Vector2(self._image.get_size()) * 0.5
        else:
            s_pos = [0, 0]
        return [c_pos[0] + s_pos[0], c_pos[1] + s_pos[1]]

    def prepare_drawing(self) -> pygame.Surface:
        return super().prepare_drawing()