import pygame
from gui.constants import UI_RESSOURCE_COLOR, UI_RESSOURCE_FONT, UI_RESSOURCE_IMAGE, UI_RESSOURCE_SFX

if not pygame.get_init():
    pygame.init()

UI_DEFAULT_RESSOURCES = {
    "fonts":{
        "regular":pygame.Font('assets/fonts/FiraCode-Regular.ttf')
    },
    "colors":{
        "default":(20, 20, 20, 230),
        "default_border":(150, 150, 150),
        "scrollbar_bg":(120, 120, 120, 128),
        "button_nothing":(100, 100, 100),
        "button_on_hover":(170, 170, 170),
        "button_on_click":(70, 70, 70)
    },
    "images":{},
    "sfx":{}
}

class UIManager():
    def __init__(self, size : list) -> None:

        self._size = size
        self.ressources = UI_DEFAULT_RESSOURCES
        self.ui_elements = []
    
    def handle_event(self, event : pygame.Event) -> None:
        for element in self.ui_elements:
            if not element.hidden:
                element.handle_event(event)
    
    def update(self, dt : float) -> None:
        for element in self.ui_elements:
            element.update(dt)
    
    def set_size(self, size : list) -> None:
        self._size = size
        for el in self.ui_elements:
            el._update_position()
    
    def add_ressource(self, ressource_type, *args):
        
        if ressource_type == UI_RESSOURCE_FONT:
            font = pygame.Font(args[0], args[1])
            self.ressources["fonts"][args[2]] = font
        elif ressource_type == UI_RESSOURCE_COLOR:
            color = args[0]
            self.ressources["colors"][args[1]] = color
        elif ressource_type == UI_RESSOURCE_IMAGE:
            image = pygame.image.load(args[0]).convert_alpha()
            self.ressources["images"][args[1]] = image
        elif ressource_type == UI_RESSOURCE_SFX:
            sfx = pygame.mixer.Sound(args[0])
            self.ressources["sfx"][args[1]] = sfx
    
    def prepare_drawing(self) -> list[pygame.Surface, tuple]:

        surfs = []

        for el in self.ui_elements:
            surf = el.prepare_drawing()
            if surf and not el.hidden:
                surfs.append((surf, el.get_position()))
        
        return surfs