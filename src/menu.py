import pygame
import math
import os

from pygame.surface import Surface as Surface

from gui import *

class Inventory(UIContainer):

    def __init__(self, camera_size : list | pygame.Vector2, manager: UIManager, container: UIContainer = None) -> None:
        super().__init__(pygame.Rect([0, 0], camera_size), manager, container)
        self._image = pygame.Surface(camera_size, pygame.SRCALPHA)
        self._image.fill(self._manager.ressources["colors"]["default"])

        self.set_hidden(True)
        self.set_align(["centerx", "centery"])
        self.add_animation(AlphaAnimation(self, .5, 0, 255), "on_show")
        self.add_animation(AlphaAnimation(self, .5, 255, 0), "on_hide")

        self.ui_slot_panel = UIPanel(pygame.Rect([0, 0], [camera_size[1], camera_size[1]]), manager, self)
        self.ui_slot_panel.set_align(["right"])
        self.ui_slot_panel.set_background_color((0, 0, 0, 32))

        self.ui_slot_panel_title = UILabel(pygame.Rect(0, 30, -1, -1), manager, "Inventory", self.ui_slot_panel)
        self.ui_slot_panel_title.set_align(["centerx"])

        self.ui_items = []

        self.ui_empty_inventory = UILabel(pygame.Rect(0, 0, -1, -1), manager, "Empty", self.ui_slot_panel)
        self.ui_empty_inventory.set_align(["centerx", "centery"])
        
        self.ui_player = UIPanel(pygame.Rect([0, 0], [camera_size[0] - camera_size[1], camera_size[1]]), manager, self)
        self.ui_player.set_background_color([0, 0, 0, 0])

        self.ui_player_visualizer = UIImage(pygame.Rect(0, 50, 250, 500), manager, self.ui_player)
        self.ui_player_visualizer.set_align(["centerx"])

        self.sides = ["south", "southeast", "east", "northeast", "north", "northwest", "west", "southwest"]
        self.side_index = 0
        for f in os.listdir("assets/player/textures/idle/"):
            surf = pygame.image.load("assets/player/textures/idle/" + f).convert_alpha()
            self.ui_player_visualizer.images[f[:-4]] = pygame.transform.scale_by(surf, 6)

        self.ui_player_visualizer.set_image(self.sides[self.side_index])
        
        self.button_A = UIButton(pygame.Rect(-75, 550, 140, 60), manager, text="A", container=self.ui_player)
        self.button_A.set_align(["centerx"])

        self.button_B = UIButton(pygame.Rect(75, 550, 140, 60), manager, text="B", container=self.ui_player)
        self.button_B.set_align(["centerx"])
    
    def update(self, dt: float):
        super().update(dt)
        if self.ui_items and not self.ui_empty_inventory.hidden:
            self.ui_empty_inventory.set_hidden(True)
        elif not self.ui_items and self.ui_empty_inventory.hidden:
            self.ui_empty_inventory.set_hidden(False)
    
    def handle_event(self, event: pygame.Event) -> None:
        super().handle_event(event)
        if event.type == UI_BUTTONCLICKED:
            if event.ui_element == self.button_A:
                self.side_index = (self.side_index - 1) % len(self.sides)
            elif event.ui_element == self.button_B:
                self.side_index = (self.side_index + 1) % len(self.sides)
            self.ui_player_visualizer.set_image(self.sides[self.side_index])