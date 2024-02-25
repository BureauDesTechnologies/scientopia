import pygame
from gui.element import UIElement, UIContainer
from gui.manager import UIManager
from gui.constants import UI_BUTTONPRESSED, UI_BUTTONHOVERED, UI_BUTTONRELEASED, UI_BUTTONCLICKED, POSITION_SCALE_FACTOR

UI_BUTTON_STATES = ["on_hover", "on_click", "nothing"]

class UIButton(UIElement):

    def __init__(self, rect : pygame.Rect, manager : UIManager, container : UIContainer = None, text : str = "") -> None:
        super().__init__(rect, manager, container)
        self._text = text
        self._font_name = "regular"

        self.button_surfaces = {}
        self._reload_graphics()

        self.state = ""
        self._update_state("nothing")
        self.clicked = False
    
    def set_font(self, font_name : str) -> None:
        self._font_name = font_name
        self._reload_graphics()
    
    def set_text(self, text : str) -> None:
        self._text = text
        self._reload_graphics()
    
    def _reload_graphics(self) -> None:

        text_surf = self._manager.ressources["fonts"][self._font_name].render(self._text, True, "white")
        blit_pos = pygame.Vector2(self._rect.size) * 0.5 - pygame.Vector2(text_surf.get_size()) * 0.5
        
        for state in UI_BUTTON_STATES:
            surf = pygame.Surface(self._rect.size)
            surf.fill(self._manager.ressources["colors"]["button_" + state])

            surf.blit(text_surf, blit_pos)

            self.button_surfaces[state] = surf

    def _update_state(self, state : str) -> None:
        if state != self.state:
            self._image = self.button_surfaces[state].copy()
        self.state = state

    def update(self, dt: float) -> None:
        super().update(dt)
    
    def handle_event(self, event: pygame.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = self.get_inner_position_from(pygame.Vector2(event.pos))
            if self._rect.collidepoint(pos):
                self._update_state("on_click")
                self.clicked = True
                pygame.event.post(pygame.Event(UI_BUTTONPRESSED, {"ui_element":self}))
        elif event.type == pygame.MOUSEBUTTONUP:
            pos = self.get_inner_position_from(pygame.Vector2(event.pos))
            if self._rect.collidepoint(pos) and self.clicked:
                self._update_state("on_hover")
                pygame.event.post(pygame.Event(UI_BUTTONCLICKED, {"ui_element":self}))
            else:
                self._update_state("nothing")
            pygame.event.post(pygame.Event(UI_BUTTONRELEASED, {"ui_element":self}))
            self.clicked = False
        elif event.type == pygame.MOUSEMOTION:
            pos = self.get_inner_position_from(pygame.Vector2(event.pos))
            if self._rect.collidepoint(pos):
                if not self.clicked:
                    self._update_state("on_hover")
                    pygame.event.post(pygame.Event(UI_BUTTONHOVERED, {"ui_element":self}))
                else:
                    self._update_state("on_click")
            else:
                self._update_state("nothing")