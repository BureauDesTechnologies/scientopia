import pygame
import json
import pathlib
import opensimplex
import random
import generation

from camera import Camera
from dataclasses import dataclass

@dataclass
class MapObject():
    o_id : int
    src : str
    center : list
    obs_width : list
    right_offset : int = 0
    image : pygame.Surface = None

class Layer:
    def __init__(self):
        self.tiles: list[tuple[pygame.Surface, pygame.Vector2]] = []
        self.based_layer: Layer = None
        self.value_based_tiles = []
        self.obstacle_tiles = []
        self.noise_generator: opensimplex.OpenSimplex = None
        self.chunks = {}
        self.generator_function = generation.generate_noise1
        self.generation_type = ""

    def build_chunk(self, tilemap: "Tilemap", chunk_pos: tuple[int, int]):
        if(self.generator_function == None):
            raise Exception("No generator function defined")

        m_datas = self.generator_function(tilemap, self, chunk_pos)

        final_map = []
        obstacles = []

        if self.generation_type == "OBJECT":
            m_objects = []

        # Selecting which tile should be used
        for j in range(1, tilemap.chunk_size + 1):
            for i in range(1, tilemap.chunk_size + 1):
                if m_datas[j][i] in self.obstacle_tiles:
                    obstacles.append((chunk_pos[0] * tilemap.chunk_size + i - 1, chunk_pos[1] * tilemap.chunk_size + j - 1))

                if self.generation_type == "PATTERN MATCHING":
                    index = self.pattern_matching(m_datas, tilemap, (i, j))
                    tile = (
                        tilemap.tileset[index],
                        pygame.Vector2(i - 1, j - 1) * tilemap.tile_size,
                    )
                    final_map.append(tile)

                elif (self.generation_type == "RANDOM" and m_datas[j][i] != 0):
                    tile = (
                        tilemap.tileset[m_datas[j][i]],
                        pygame.Vector2(i - 1, j - 1) * tilemap.tile_size,
                    )
                    final_map.append(tile)
                    
                elif (self.generation_type == "OBJECT" and m_datas[j][i] != -1):
                    obstacle = pygame.Vector2(chunk_pos[0] * tilemap.chunk_size + i - 1, chunk_pos[1] * tilemap.chunk_size + j - 1)
                    obs_width = tilemap.m_objects[m_datas[j][i]].obs_width
                    for l in range(-obs_width[1], obs_width[1]+1):
                        for k in range(-obs_width[0], obs_width[0]+1):
                            obs = pygame.Vector2(chunk_pos[0] * tilemap.chunk_size + i - 1 + k, chunk_pos[1] * tilemap.chunk_size + j - 1 + l)
                            obstacles.append(obs)

                    # Centralisation de l'objet
                    obj_pos = pygame.Vector2(i - 1, j - 1) * tilemap.tile_size
                    obj_pos += tilemap.chunk_size * tilemap.tile_size * pygame.Vector2(chunk_pos)
                    obj_pos += pygame.Vector2(tilemap.tile_size) * 0.5
                    obj_pos -= pygame.Vector2(tilemap.m_objects[m_datas[j][i]].center)

                    obj = [
                        tilemap.m_objects[m_datas[j][i]].image,
                        obj_pos,
                        obstacle * tilemap.tile_size + pygame.Vector2(tilemap.m_objects[m_datas[j][i]].right_offset, 0)
                    ]

                    m_objects.append(obj)


        # Génération de la surface du chunk, cette partie devrait à priori rester inchangé
        if not self.generation_type == "OBJECT":
            chunk_surface = pygame.Surface(
                pygame.Vector2(1, 1) * (tilemap.chunk_size * tilemap.tile_size),
                pygame.SRCALPHA,
            )
            chunk_surface.fblits(final_map)
            self.chunks[chunk_pos] = {"surface":chunk_surface, "obstacles":obstacles}
        else:
            self.chunks[chunk_pos] = {"objects":m_objects, "obstacles":obstacles}

    def pattern_matching(self, m_datas, tilemap, pos):
        i, j = pos
        if m_datas[j][i] in self.value_based_tiles:
            indices = tilemap.get_pattern(
                tuple(m_datas[j][i] for _ in range(8)), m_datas[j][i]
            )
        else:
            pattern = (
                m_datas[j - 1][i],
                m_datas[j - 1][i + 1],
                m_datas[j][i + 1],
                m_datas[j + 1][i + 1],
                m_datas[j + 1][i],
                m_datas[j + 1][i - 1],
                m_datas[j][i - 1],
                m_datas[j - 1][i - 1],
            )
            indices = tilemap.get_pattern(pattern, m_datas[j][i])
        return random.choice(indices)

class Tilemap:
    def __init__(self):
        self.chunk_size = 16  # in number of tile
        # The tile size
        self.tile_size = 16

        self.tileset: list[pygame.Surface] = []

        self.layers: dict[str, Layer] = {"foreground": Layer()}
        self.m_objects = {}

        self.thresholds = {0: 0, 1: None}
        self.patterns = {}
        self.value_based_tiles = []

        self.player = None

    def _find_similar_pattern(self, pattern: tuple[int]) -> tuple[int]:
        for p in self.patterns:
            s = []
            for i, v in enumerate(pattern):
                if v == p[i] or p[i] == 0:
                    s.append(p[i])

            if len(s) == 8:
                return tuple(s)

        return None

    def get_pattern(self, pattern: tuple[int], original_value: int) -> list[int]:
        index = self.patterns.get(pattern, None)

        if index != None:
            return index

        p = self._find_similar_pattern(pattern)

        if p == None:
            return self.patterns[tuple(original_value for _ in range(8))]
        else:
            return self.patterns[p]

    def load_tileset(self, path) -> None:
        tile_list = []

        path_obj = pathlib.Path(path)

        with open(path_obj) as reader:
            json_obj = json.load(reader)

            tile_width, tile_height = json_obj["tilewidth"], json_obj["tileheight"]

            image = pygame.image.load(
                path_obj.parent.joinpath(json_obj["image"])
            ).convert_alpha()

            for y in range(json_obj["imageheight"] // tile_height):
                for x in range(json_obj["columns"]):
                    tile_list.append(
                        image.subsurface(
                            pygame.Rect(
                                [x * tile_width, y * tile_height],
                                [tile_width, tile_height],
                            )
                        )
                    )

            if not "wangsets" in json_obj:
                self.tileset.extend(tile_list)
                return

            for wangset in json_obj["wangsets"]:
                for pattern in wangset["wangtiles"]:
                    p = tuple(pattern["wangid"])
                    if not p in self.patterns:
                        self.patterns[p] = [pattern["tileid"]]
                    else:
                        self.patterns[p].append(pattern["tileid"])

        self.tileset.extend(tile_list)
    
    def load_objects(self, path) -> None:

        path_obj = pathlib.Path(path)

        with open(path_obj) as reader:
            json_obj = json.load(reader)

            for obj in json_obj["objects"]:
                m_obj = MapObject(obj["id"], obj["src"], obj["center"], obj["width"])
                m_obj.image = pygame.image.load(m_obj.src).convert_alpha()
                m_obj.right_offset = m_obj.image.get_width() - m_obj.center[0]
                self.m_objects[obj["id"]] = m_obj

    def generate(self, radius=3, seed=0) -> None:
        """
        Generates the map
        """
        open_simplex_a = opensimplex.OpenSimplex(seed)

        self.layers["foreground"].noise_generator = open_simplex_a

        for j in range(-radius, radius):
            for i in range(-radius, radius):
                for layer in self.layers:
                    self.layers[layer].build_chunk(self, (i, j))
    
    def get_obstacles(self):

        player_pos = int(
            self.player.hitbox.x // (self.chunk_size * self.tile_size)
        ), int(self.player.hitbox.y // (self.chunk_size * self.tile_size))

        obstacles = []
        for layer in self.layers.values():
            for j in range(player_pos[1] - 2, player_pos[1] + 3):
                for i in range(player_pos[0] - 3, player_pos[0] + 3):
                    if (i, j) in layer.chunks:
                        obstacles.extend(layer.chunks[(i, j)]["obstacles"])
        
        return obstacles
    
    def get_objects(self):

        player_pos = int(
            self.player.hitbox.x // (self.chunk_size * self.tile_size)
        ), int(self.player.hitbox.y // (self.chunk_size * self.tile_size))

        objects = []
        for layer in self.layers.values():

            if not layer.generation_type == "OBJECT":
                continue

            for j in range(player_pos[1] - 2, player_pos[1] + 2):
                for i in range(player_pos[0] - 2, player_pos[0] + 3):
                    if (i, j) in layer.chunks:
                        objects.extend(layer.chunks[(i, j)]["objects"])
        
        return objects


    def draw(self, camera: Camera) -> None:
        """
        This method draws the tilemap
        """
        player_pos = int(
            self.player.hitbox.x // (self.chunk_size * self.tile_size)
        ), int(self.player.hitbox.y // (self.chunk_size * self.tile_size))

        for layer in self.layers.values():
            offseted_layer = []

            for j in range(player_pos[1] - 2, player_pos[1] + 2):
                for i in range(player_pos[0] - 3, player_pos[0] + 3):

                    if (i, j) not in layer.chunks:
                        layer.build_chunk(self, (i, j))
                    if not layer.generation_type == "OBJECT":
                        offseted_layer.append(
                            (
                                layer.chunks[(i, j)]["surface"],
                                round(
                                    pygame.Vector2((i, j))
                                    * self.chunk_size
                                    * self.tile_size
                                    - pygame.Vector2(camera.rect.topleft)
                                ),
                            )
                        )

            camera.draw(offseted_layer)
