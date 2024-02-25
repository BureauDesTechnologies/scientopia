import pygame
import math
import pathlib
import gif_pygame
import pathfinding

from camera import Camera


SIDES = {(1, 0):"east",
         (1, -1):"northeast",
         (0, -1):"north",
         (-1, -1):"northwest",
         (-1, 0):"west",
         (-1, 1):"southwest",
         (0, 1):"south",
         (1, 1):"southeast",
         (0, 0):"None"
         }

def load_player_assets(path : str):

    xpath = pathlib.Path(path)
    
    ressources = {}

    for p in xpath.iterdir():
        if p.name == "animations":
            anims = {}
            for anim in p.iterdir():
                animation = {}
                for side in anim.iterdir():
                    gif = gif_pygame.load(side.as_posix())
                    animation[side.stem] = gif
                anims[anim.name] = animation
            ressources["animations"] = anims
        elif p.name == "textures":
            texs = {}
            for tex in p.iterdir():
                texture = {}
                for side in tex.iterdir():
                    texture[side.stem] = pygame.image.load(side.as_posix()).convert_alpha()
                texs[tex.name] = texture
            ressources["textures"] = texs

    return ressources


class Player:
    def __init__(self):
        self.hitbox = pygame.FRect(0, 0, 20, 28)
        self.cell_offset = pygame.Vector2(8, 10)
        self.set_cell_position([-20, 0])

        self.speed = 100
        self.jumping = False

        self.ressources = load_player_assets("./assets/player/")
        self.image = self.ressources["textures"]["idle"]["south"]
        self.animation = None
        self.direction = "south"

        self.path = pathfinding.PathData()
        self.walked_distance_timer = 0
        self.distance_remaining = 0
        self.current_cell = None
        self.reached_destination = True
    
    def set_cell_position(self, position):
        self.cell_position = position
        self.hitbox.midbottom = pygame.Vector2(self.cell_position) * 16 + self.cell_offset

    def update(self, dt: float):

        direction = pygame.Vector2()
        if self.path.cells:
            if self.distance_remaining > 0:
                self.distance_remaining = self.distance_remaining - self.speed * dt
            else:
                self.set_cell_position(self.path.cells[0].pos)
                self.path.cells = []
                self.current_cell = None
        else:   
            self.reached_destination = True
        

        if self.path.cells and not self.current_cell:
            self.current_cell = self.path.cells.pop(0)

        for cell in self.path.cells:
            if cell.distance > self.distance_remaining:
                self.current_cell = self.path.cells.pop(0)
                if cell.pos != self.cell_position:
                    self.set_cell_position(cell.pos)
                
            else:
                break
        
        if self.current_cell and self.current_cell.distance:
            direction = pygame.Vector2(self.current_cell.direction)
            offset = (self.current_cell.distance - self.distance_remaining)
            cell_direction = pygame.Vector2(self.current_cell.direction).normalize()
            self.hitbox.midbottom = pygame.Vector2(self.cell_position) * 16 + self.cell_offset + cell_direction * offset

        side = SIDES[tuple(direction)]

        if side == "None":
            self.animation = None
            self.image = self.ressources["textures"]["idle"][self.direction]
        else:
            self.direction = side
            self.animation = self.ressources["animations"]["walking"][self.direction]

        if direction:
            direction.normalize_ip()
    
    def prepare_drawing(self):
        pos = pygame.Vector2(self.hitbox.topleft)
        image = self.image if not self.animation else self.animation.blit_ready()
        return [image, pos, pygame.Vector2(self.hitbox.midbottom)]


    def draw(self, camera: Camera):
        blit_data = self.prepare_drawing()[:2]
        blit_data[1] -= pygame.Vector2(camera.rect.topleft)

        camera.draw([tuple(blit_data)])
