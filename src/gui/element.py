import pygame
from pygame.surface import Surface as Surface

from gui.manager import UIManager
from gui.constants import UI_ANIMATIONENDED
from gui.animation import Animation

class UIElement():

    def __init__(self, rect : pygame.Rect, manager : UIManager, container : "UIContainer" = None) -> None:
        
        self._manager = manager
        self._container = container
        self._not_aligned_position = rect.topleft
        self._rect = rect
        self._image = None
        self.hidden = False

        if not container:
            self._manager.ui_elements.append(self)
        else:
            self._container.ui_elements.append(self)
        
        self._align = []

        # MoveAnimation(1.0, pygame.Vector2(), pygame.Vector2(0, 350), ease_in_sin, lambda : hide(self))
        # MoveAnimation(1.5, pygame.Vector2(0, 350), pygame.Vector2(), ease_out_sin)
        self.current_animation = None
        self.animations = {
            "on_hide":None,
            "on_show":None
        }
    
    def add_animation(self, animation : Animation, name : str):
        animation.name = name
        self.animations[name] = animation
    
    def update(self, dt : float):
        if not self.current_animation:
            return
        self.current_animation.update(dt)
        if self.current_animation.finished:
            self.current_animation.reset()
            pygame.event.post(pygame.Event(UI_ANIMATIONENDED, {"ui_element":self, "animation_name":self.current_animation.name}))
            if self.current_animation.name == "on_hide":
                self.hidden = True
            self.current_animation = None
    
    def set_animation(self, animation_name : str) -> None:
        if not self.current_animation:
            self.current_animation = self.animations[animation_name]
            if self.current_animation:
                self.current_animation.name = animation_name
    
    def set_hidden(self, hidden : bool):
        if hidden:
            self.set_animation("on_hide")
            if not self.current_animation:
                self.hidden = True
        else:
            self.set_animation("on_show")
            self.hidden = hidden
    
    def set_position(self, pos : list | pygame.Vector2) -> None:
        self._not_aligned_position = pos
        self._update_position()
    
    def set_size(self, size : list | pygame.Vector2) -> None:
        self._rect.size = size
        self._reload_graphics()
    
    def set_align(self, aligns : list) -> None:
        self._align = aligns
        self._update_position()
    
    def get_position(self) -> tuple:
        return self._rect.topleft
    
    def get_size(self) -> tuple:
        return self._rect.size
    
    def _update_position(self) -> None:
        pos = list(self._not_aligned_position).copy()

        if "right" in self._align:
            if not self._container:
                pos[0] = self._manager._size[0] - pos[0] - self._rect.w
            else:
                pos[0] = self._container._rect.size[0] - pos[0] - self._rect.w
        elif "centerx" in self._align:
            if not self._container:
                pos[0] = self._manager._size[0] * 0.5 - self._rect.w * 0.5 + pos[0]
            else:
                pos[0] = self._container._rect.size[0] * 0.5 - self._rect.w * 0.5 + pos[0]
        
        if "bottom" in self._align:
            if not self._container:
                pos[1] = self._manager._size[1] - pos[1] - self._rect.h
            else:
                pos[1] = self._container._rect.size[1] - pos[1] - self._rect.h
        elif "centery" in self._align:
            if not self._container:
                pos[1] = self._manager._size[1] * 0.5 - self._rect.h * 0.5 + pos[1]
            else:
                pos[1] = self._container._rect.size[1] * 0.5 - self._rect.h * 0.5 + pos[1]
        
        self._rect.topleft = pos
    
    def get_inner_position_from(self, pos : pygame.Vector2) -> pygame.Vector2:
        if self._container:
            return self._container.get_inner_position_from(pos - pygame.Vector2(self._container.get_position()))
        else:
            return pygame.Vector2(pos)
    
    def _reload_graphics(self) -> None:
        pass
    
    def handle_event(self, event : pygame.Event) -> None:
        pass

    def prepare_drawing(self) -> pygame.Surface:
        return self._image

class UIContainer(UIElement):

    def __init__(self, rect: pygame.Rect, manager: UIManager, container : "UIContainer" = None) -> None:
        super().__init__(rect, manager, container)
        self._container_image = None
        self.ui_elements = []

    def handle_event(self, event: pygame.Event) -> None:
        
        for el in self.ui_elements:
            if not el.hidden:
                el.handle_event(event)
    
    def set_background_color(self, color):
        self._image = pygame.Surface(self._image.get_size(), pygame.SRCALPHA)
        self._image.fill(color)
    
    def update(self, dt: float):
        super().update(dt)
        for el in self.ui_elements:
            el.update(dt)

    def prepare_drawing(self) -> Surface:
        self._container_image = self._image.copy()
        
        surfs = []

        for el in self.ui_elements:
            surf = el.prepare_drawing()
            if surf and not el.hidden:
                surfs.append((surf, el.get_position()))
        
        self._container_image.blits(surfs)
        return self._container_image

    