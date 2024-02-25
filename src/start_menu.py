import pygame
import scene

from gui import *


class StartMenu(scene.Scene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self.ui_manager = UIManager(pygame.display.get_window_size())
        self.ui_manager.add_ressource(UI_RESSOURCE_FONT, "assets/fonts/FiraCode-Regular.ttf", 50, "large")

        self.game_title = UILabel(pygame.Rect(0, 100, -1, -1), self.ui_manager, "Scientopia")
        self.game_title.set_align(["centerx"])
        self.game_title.set_font("large")

        self.play_button = UIButton(pygame.Rect(0, 100, 200, 75), self.ui_manager, text="Play")
        self.play_button.set_align(["centerx", "centery"])

    def events(self, event: pygame.Event):
        if event.type == UI_BUTTONCLICKED:
            self.scene_manager.set_scene("game")

        self.ui_manager.handle_event(event)

    def update(self, clock: pygame.Clock):
        self.screen.fill("black")

        dt = clock.tick() / 1000

        self.ui_manager.update(dt)
        self.screen.blits(self.ui_manager.prepare_drawing())
