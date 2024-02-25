import pygame
import scene
import gif_pygame
import pathfinding
import gui
import bisect

from tilemap import Tilemap,Layer
from player import Player
from camera import Camera
from menu import Inventory
from generation import *



class Game(scene.Scene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)

        self.camera = Camera(pygame.Vector2(pygame.display.get_window_size()))
        self.game_map = Tilemap()

        self.player = Player()
        self.player_moveable = True

        self.draw_map = True
        ui_manager_size = pygame.Vector2(self.camera.rect.size) * 2
        self.ui_manager = gui.UIManager(ui_manager_size)

        self.ui_inventory = Inventory(ui_manager_size, self.ui_manager)

        self.debug_surf = pygame.Surface([16, 16])
        self.debug_surf.fill("green")

    def start(self):

        self.game_map.player = self.player
        self.game_map.layers["foreground"].value_based_tiles.append(1)
        self.game_map.layers["foreground"].generation_type = "PATTERN MATCHING"
        self.game_map.layers["foreground"].obstacle_tiles.append(3)

        self.game_map.load_tileset("./assets/tilesets/tileset_1.tsj")
        self.game_map.load_objects("./assets/obj_settings.json")

        self.game_map.layers["flowers"] = Layer()
        self.game_map.layers["flowers"].generation_type = "RANDOM"
        self.game_map.layers["flowers"].generator_function = generate_flowers

        self.game_map.layers["trees"] = Layer()
        self.game_map.layers["trees"].generation_type = "OBJECT"
        self.game_map.layers["trees"].generator_function = generate_trees

        self.game_map.generate(seed=1)


        # Working on
        self.player_dest_surface = pygame.image.load("./assets/target_cell.png").convert_alpha()
        self.player_dest_arrow = gif_pygame.load("./assets/target_arrow.gif")
        gif_pygame.transform.convert_alpha(self.player_dest_arrow)
        self.player_dest = pygame.Vector2(0, 0)

        self.path_block = pygame.Surface([16, 16], pygame.SRCALPHA)
        self.path_block.fill((0, 0, 200, 64))
        # pygame.mouse.set_visible(False)

    def events(self, event: pygame.Event):

        if event.type == pygame.MOUSEBUTTONDOWN and self.player.reached_destination and self.player_moveable:
            mouse_pos = pygame.Vector2(event.pos)
            # 2 c'est le coefficient de zoom de la caméra, 16 la taille des tuiles
            mouse_pos /= 2
            mouse_pos += pygame.Vector2(self.camera.rect.topleft)
            mouse_pos //= 16
            self.player_dest = mouse_pos
            self.player.path = pathfinding.find_way(tuple(self.player.cell_position), tuple(mouse_pos), self.game_map.get_obstacles())
            self.player.distance_remaining = self.player.path.distance
            self.player.reached_destination = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                if not self.ui_inventory.current_animation:
                    self.ui_inventory.set_hidden(not self.ui_inventory.hidden)
        
        elif event.type == gui.UI_ANIMATIONENDED:
            if event.animation_name == "on_hide":
                self.player_moveable = True
            elif event.animation_name == "on_show":
                self.player_moveable = False

        self.ui_manager.handle_event(event)

    def update(self, clock: pygame.Clock):

        dt = clock.tick() / 1000
        # draw part

        self.camera.clear()

        self.player.update(dt)

        self.camera.rect.x += (
            (self.player.hitbox.centerx - self.camera.rect.centerx) * 3 * dt
        )
        self.camera.rect.y += (
            (self.player.hitbox.centery - self.camera.rect.centery) * 3 * dt
        )

        self.ui_manager.update(dt)

        self.game_map.draw(self.camera)

        objects = self.game_map.get_objects() + [self.player.prepare_drawing()]
        l_objs = []
        for obj in objects:
            bisect.insort(l_objs, [obj[0], round(obj[1] - pygame.Vector2(self.camera.rect.topleft)), obj[2]], key= lambda o : (o[2][1], o[2][0]))
        for obj in l_objs:
            obj.pop(-1)
        self.camera.draw(l_objs)

        if not self.player.reached_destination:
            self.camera.draw([(self.player_dest_surface, self.player_dest * 16 - pygame.Vector2(self.camera.rect.topleft))])
            self.camera.draw([(self.player_dest_arrow.blit_ready(), self.player_dest * 16 - pygame.Vector2(self.camera.rect.topleft) - pygame.Vector2(0, 8))])

        # blocks = []
        # for block in self.game_map.get_obstacles():
        #     blocks.append((self.debug_surf, pygame.Vector2(block) * 16 - pygame.Vector2(self.camera.rect.topleft)))
        # self.camera.draw(blocks)

        # self.player.draw(self.camera)
        self.camera.display_on_screen()
        self.camera.draw(self.ui_manager.prepare_drawing(), on_screen=True)

        pygame.display.set_caption(f"FPS : {round(clock.get_fps(), 2)}")
