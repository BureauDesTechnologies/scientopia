import pygame
from gui.element import UIElement, UIContainer
from gui.manager import UIManager

class UILabel(UIElement):
    def __init__(self, rect: pygame.Rect, manager: UIManager, text : str, container : UIContainer = None) -> None:
        super().__init__(rect, manager, container)

        self._text = text
        self._font_name = "regular"
        self._dynamic_resize = rect.w == -1 or rect.h == -1
        self._reload_graphics()
    
    def set_font(self, font_name : str) -> None:
        self._font_name = font_name
        self._reload_graphics()
    
    def set_text(self, text : str) -> None:
        self._text = text
        self._reload_graphics()
    
    def update(self, dt: float) -> None:
        return super().update(dt)

    def handle_event(self, event: pygame.Event) -> None:
        return super().handle_event(event)
    
    def _reload_graphics(self) -> None:
        
        text_surf = self._manager.ressources["fonts"][self._font_name].render(self._text, True, "white")
        blit_pos = pygame.Vector2(self._rect.size) * 0.5 - pygame.Vector2(text_surf.get_size()) * 0.5

        if not self._dynamic_resize:
            surf = pygame.Surface(self._rect.size, pygame.SRCALPHA)
            surf.blit(text_surf, blit_pos)
            self._image = surf
        else:
            self._image = text_surf
            self._rect.size = self._image.get_size()
        
        self._update_position()