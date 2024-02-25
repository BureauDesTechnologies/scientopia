import pygame
from gui.element import UIContainer
from gui.button import UIButton
from gui.manager import UIManager
from gui.constants import *

class UIScrollbar(UIContainer):
    def __init__(self, rect: pygame.Rect, manager: UIManager, container: UIContainer = None) -> None:
        super().__init__(rect, manager, container)

        self._image = pygame.Surface(self._rect.size, pygame.SRCALPHA)
        self._image.fill(self._manager.ressources["colors"]["scrollbar_bg"])
        self._container_image = self._image.copy()

        self.value = 0

        self._bar = UIButton(pygame.Rect([0, 0], [rect.w, rect.h * 0.5]), self._manager, self)
        self._bar.button_surfaces["on_click"] = self._bar.button_surfaces["on_hover"] = self._bar.button_surfaces["nothing"].copy()
        self._pressed = False
        self._offset_bar = 0
    
    def handle_event(self, event: pygame.Event) -> None:
        
        super().handle_event(event)

        if event.type == UI_BUTTONPRESSED:
            if event.ui_element == self._bar:
                m_pos = self.get_inner_position_from(pygame.Vector2(pygame.mouse.get_pos()))
                self._offset_bar = m_pos[1] - self._bar.get_position()[1]
                self._pressed = True
        elif event.type == UI_BUTTONRELEASED:
            if event.ui_element == self._bar:
                self._pressed = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self._pressed:
                m_pos = self.get_inner_position_from(pygame.Vector2(event.pos))
                y_pos = pygame.math.clamp(m_pos[1] - self._offset_bar, 0, self.get_size()[1] - self._bar.get_size()[1])
                self._bar.set_position([0, y_pos])



