import pygame
import sys
import os
import math
import random
from pathlib import Path

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 16
SCALE = 2
FPS = 60

CLOCK_ICON_SIZE = 128
CLOCK_DISPLAY_SIZE = 800
CLOCK_CENTER_X = SCREEN_WIDTH // 2
CLOCK_CENTER_Y = SCREEN_HEIGHT // 2

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (51, 153, 51)
BROWN = (128, 102, 77)
BLUE = (51, 102, 204)
GRAY = (128, 128, 128)
RED = (200, 50, 50)
DARK_BLUE = (30, 30, 100)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Little Cat Time Adventure - Faiz")
        self.clock = pygame.time.Clock()
        self.running = True
        
        pygame.mixer.init()
        
        self.load_sprites()
        self.load_map()
        self.load_clock()
        self.load_sounds()
        
        self.player = {
            'x': 240,
            'y': 160,
            'speed': 100,
            'width': 16,
            'height': 16,
            'direction': 'down',
            'state': 'idle',
            'animation_timer': 0,
            'animation_frame': 0
        }
        
        self.camera_x = 0
        self.camera_y = 0
        
        self.animation_speed = 0.3
        
        self.clock_ui_active = False
        self.hour_angle = 0
        self.minute_angle = 0
        self.dragging_hand = None
        self.clock_icon_rect = pygame.Rect(10, 10, CLOCK_ICON_SIZE, CLOCK_ICON_SIZE)
        
        self.trees = [
            {'x': 2, 'y': 50},
            {'x': 100, 'y': 230},
            {'x': 350, 'y': 150},
            {'x': 350, 'y': 250},
        ]
        self.load_tree()
        
        self.bushes = [
            {'x': 220, 'y': 270, 'picked': False},
            {'x': 280, 'y': 270, 'picked': False},
            {'x': 250, 'y': 270, 'picked': False},
        ]
        self.load_bush()
        self.load_fruit()
        
        self.trunks = [
            {'x': 400, 'y': 100, 'cut': False},
            {'x': 50, 'y': 150, 'cut': False},
        ]
        self.load_trunk()
        
        self.flowers = [
            {'x': 120, 'y': 100, 'watered': False},
            {'x': 120, 'y': 70, 'watered': False},
            {'x': 150, 'y': 70, 'watered': False},
            {'x': 150, 'y': 100, 'watered': False},
            {'x': 180, 'y': 70, 'watered': False},
            {'x': 180, 'y': 100, 'watered': False},
        ]
        self.load_flower()
        
        self.mushrooms = [
            {'x': 160, 'y': 180, 'removed': False},
            {'x': 450, 'y': 180, 'removed': False},
            {'x': 20, 'y': 280, 'removed': False},
            {'x': 350, 'y': 80, 'removed': False},
        ]
        self.load_mushroom()
        
        self.watering = False
        self.watering_side = None
        self.watering_timer = 0
        self.watering_duration = 1.0
        
        self.picking = False
        self.picking_timer = 0
        self.picking_duration = 3.0
        self.fruits_picked = 0
        
        self.cutting = False
        self.cutting_side = None
        self.cutting_timer = 0
        self.cutting_duration = 1.5
        self.trunks_cut = 0
        
        self.flower_watering = False
        self.flower_watering_side = None
        self.flower_watering_timer = 0
        self.flower_watering_duration = 1.0
        self.flowers_watered = 0
        
        self.mushroom_cutting = False
        self.mushroom_cutting_side = None
        self.mushroom_cutting_timer = 0
        self.mushroom_cutting_duration = 1.5
        self.mushrooms_removed = 0
        
        self.missions = [
            {
                'id': 1,
                'title': 'Siram pohon pada jam 1',
                'description': 'Set jam ke 01:00 lalu siram pohon',
                'completed': False,
                'required_hour': 1
            },
            {
                'id': 2,
                'title': 'Petik 3 buah dari semak',
                'description': 'Set jam ke 03:00 lalu petik buah',
                'completed': False,
                'required_hour': 3
            },
            {
                'id': 3,
                'title': 'Singkirkan 2 batang kayu',
                'description': 'Set jam ke 05:00 lalu singkirkan kayu',
                'completed': False,
                'required_hour': 5
            },
            {
                'id': 4,
                'title': 'Siram bunga',
                'description': 'Set jam ke 08:00 lalu siram bunga',
                'completed': False,
                'required_hour': 8
            },
            {
                'id': 5,
                'title': 'Singkirkan semua jamur',
                'description': 'Set jam ke 09:00 lalu singkirkan jamur',
                'completed': False,
                'required_hour': 9
            }
        ]
        random.shuffle(self.missions)
        for i, mission in enumerate(self.missions, 1):
            mission['id'] = i
        
        self.mission_box_rect = pygame.Rect(150, 10, 300, 300)
        self.play_again_button_rect = pygame.Rect(300, 450, 200, 60)
        
        self.notification_text = ""
        self.notification_timer = 0
        self.notification_duration = 3.0
        
    def load_sprites(self):
        self.sprites = {}
        sprite_folder = 'char'
        
        sprite_mapping = {
            'idle1.png': 'idle-front1',
            'idle2.png': 'idle-front2',
            'idle-back1.png': 'idle-back1',
            'idle-back2.png': 'idle-back2',
            'idle-left1.png': 'idle-left1',
            'idle-left2.png': 'idle-left2',
            'idle-right1.png': 'idle-right1',
            'idle-right2.png': 'idle-right2',
            'walk1.png': 'walk-front1',
            'walk2.png': 'walk-front2',
            'walk-back1.png': 'walk-back1',
            'walk-back2.png': 'walk-back2',
            'walk-left1.png': 'walk-left1',
            'walk-left2.png': 'walk-left2',
            'walk-right1.png': 'walk-right1',
            'walk-right2.png': 'walk-right2'
        }
        
        sprite_paths = {filename: os.path.join(sprite_folder, filename) for filename in sprite_mapping.keys()}
        all_exist = all(os.path.exists(path) for path in sprite_paths.values())
        
        if all_exist:
            print(f"Loading directional sprites from {sprite_folder}/ folder...")
            for filename, sprite_name in sprite_mapping.items():
                sprite_path = sprite_paths[filename]
                self.sprites[sprite_name] = pygame.image.load(sprite_path).convert_alpha()
        else:
            print("Generating directional sprites programmatically...")
            self.generate_sprites()
        
        for key in self.sprites:
            self.sprites[key] = pygame.transform.scale(
                self.sprites[key], 
                (16 * SCALE, 16 * SCALE)
            )
        
        self.load_watering_sprites()
    
    def generate_sprites(self):
        sprite_size = 16
        
        skin = (255, 204, 153)
        shirt = (51, 102, 204)
        pants = (77, 51, 26)
        
        for i in range(1, 3):
            sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
            pygame.draw.rect(sprite, skin, (6, 2, 4, 4))
            pygame.draw.rect(sprite, shirt, (5, 6, 6, 5))
            pygame.draw.rect(sprite, pants, (5, 11, 3, 5))
            pygame.draw.rect(sprite, pants, (8, 11, 3, 5))
            self.sprites[f'idle-front{i}'] = sprite
        
        for i in range(1, 3):
            sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
            pygame.draw.circle(sprite, skin, (8, 3), 2)
            pygame.draw.rect(sprite, shirt, (5, 5, 6, 6))
            pygame.draw.rect(sprite, pants, (5, 11, 3, 5))
            pygame.draw.rect(sprite, pants, (8, 11, 3, 5))
            self.sprites[f'idle-back{i}'] = sprite
        
        for i in range(1, 3):
            sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
            pygame.draw.rect(sprite, skin, (7, 2, 3, 4))
            pygame.draw.rect(sprite, shirt, (6, 6, 5, 5))
            pygame.draw.rect(sprite, pants, (6, 11, 2, 5))
            pygame.draw.rect(sprite, pants, (8, 11, 2, 5))
            self.sprites[f'idle-left{i}'] = sprite
        
        for i in range(1, 3):
            sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
            pygame.draw.rect(sprite, skin, (6, 2, 3, 4))
            pygame.draw.rect(sprite, shirt, (5, 6, 5, 5))
            pygame.draw.rect(sprite, pants, (6, 11, 2, 5))
            pygame.draw.rect(sprite, pants, (8, 11, 2, 5))
            self.sprites[f'idle-right{i}'] = sprite
        
        sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        pygame.draw.rect(sprite, skin, (6, 2, 4, 4))
        pygame.draw.rect(sprite, shirt, (5, 6, 6, 5))
        pygame.draw.rect(sprite, pants, (4, 11, 3, 5))
        pygame.draw.rect(sprite, pants, (9, 12, 3, 4))
        self.sprites['walk-front1'] = sprite
        
        sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        pygame.draw.rect(sprite, skin, (6, 2, 4, 4))
        pygame.draw.rect(sprite, shirt, (5, 6, 6, 5))
        pygame.draw.rect(sprite, pants, (9, 11, 3, 5))
        pygame.draw.rect(sprite, pants, (4, 12, 3, 4))
        self.sprites['walk-front2'] = sprite
        
        sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        pygame.draw.circle(sprite, skin, (8, 3), 2)
        pygame.draw.rect(sprite, shirt, (5, 5, 6, 6))
        pygame.draw.rect(sprite, pants, (4, 11, 3, 5))
        pygame.draw.rect(sprite, pants, (9, 12, 3, 4))
        self.sprites['walk-back1'] = sprite
        
        sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        pygame.draw.circle(sprite, skin, (8, 3), 2)
        pygame.draw.rect(sprite, shirt, (5, 5, 6, 6))
        pygame.draw.rect(sprite, pants, (9, 11, 3, 5))
        pygame.draw.rect(sprite, pants, (4, 12, 3, 4))
        self.sprites['walk-back2'] = sprite
        
        sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        pygame.draw.rect(sprite, skin, (7, 2, 3, 4))
        pygame.draw.rect(sprite, shirt, (6, 6, 5, 5))
        pygame.draw.rect(sprite, pants, (5, 11, 3, 5))
        pygame.draw.rect(sprite, pants, (8, 12, 2, 4))
        self.sprites['walk-left1'] = sprite
        
        sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        pygame.draw.rect(sprite, skin, (7, 2, 3, 4))
        pygame.draw.rect(sprite, shirt, (6, 6, 5, 5))
        pygame.draw.rect(sprite, pants, (8, 11, 3, 5))
        pygame.draw.rect(sprite, pants, (5, 12, 2, 4))
        self.sprites['walk-left2'] = sprite
        
        sprite = self.sprites['walk-right1']
        
        sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        pygame.draw.rect(sprite, skin, (6, 2, 3, 4))
        pygame.draw.rect(sprite, shirt, (5, 6, 5, 5))
        pygame.draw.rect(sprite, pants, (6, 11, 3, 5))
        pygame.draw.rect(sprite, pants, (8, 12, 2, 4))
        self.sprites['walk-right2'] = sprite
    
    def load_watering_sprites(self):
        sprite_folder = 'char'
        watering_files = ['watering-left1.png', 'watering-left2.png', 
                         'watering-right1.png', 'watering-right2.png']
        
        sprite_paths = [os.path.join(sprite_folder, f) for f in watering_files]
        all_exist = all(os.path.exists(p) for p in sprite_paths)
        
        if all_exist:
            print(f"Loading watering sprites from {sprite_folder}/ folder...")
            for sprite_file, sprite_path in zip(watering_files, sprite_paths):
                sprite_name = sprite_file.replace('.png', '')
                self.sprites[sprite_name] = pygame.image.load(sprite_path).convert_alpha()
                self.sprites[sprite_name] = pygame.transform.scale(
                    self.sprites[sprite_name], 
                    (16 * SCALE, 16 * SCALE)
                )
        else:
            print("Generating watering sprites programmatically...")
            self.generate_watering_sprites()
    
    def generate_watering_sprites(self):
        sprite_size = 16
        
        skin = (255, 204, 153)
        shirt = (51, 102, 204)
        pants = (77, 51, 26)
        water_can = (150, 150, 150)
        
        wl1 = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        pygame.draw.rect(wl1, skin, (6, 2, 4, 4))
        pygame.draw.rect(wl1, shirt, (5, 6, 6, 5))
        pygame.draw.rect(wl1, pants, (5, 11, 3, 5))
        pygame.draw.rect(wl1, pants, (8, 11, 3, 5))
        pygame.draw.rect(wl1, water_can, (2, 5, 3, 4))
        self.sprites['watering-left1'] = pygame.transform.scale(wl1, (16 * SCALE, 16 * SCALE))
        
        wl2 = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        pygame.draw.rect(wl2, skin, (6, 2, 4, 4))
        pygame.draw.rect(wl2, shirt, (5, 6, 6, 5))
        pygame.draw.rect(wl2, pants, (5, 11, 3, 5))
        pygame.draw.rect(wl2, pants, (8, 11, 3, 5))
        pygame.draw.rect(wl2, water_can, (1, 6, 3, 4))
        self.sprites['watering-left2'] = pygame.transform.scale(wl2, (16 * SCALE, 16 * SCALE))
        
        wr1 = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        pygame.draw.rect(wr1, skin, (6, 2, 4, 4))
        pygame.draw.rect(wr1, shirt, (5, 6, 6, 5))
        pygame.draw.rect(wr1, pants, (5, 11, 3, 5))
        pygame.draw.rect(wr1, pants, (8, 11, 3, 5))
        pygame.draw.rect(wr1, water_can, (11, 5, 3, 4))
        self.sprites['watering-right1'] = pygame.transform.scale(wr1, (16 * SCALE, 16 * SCALE))
        
        wr2 = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        pygame.draw.rect(wr2, skin, (6, 2, 4, 4))
        pygame.draw.rect(wr2, shirt, (5, 6, 6, 5))
        pygame.draw.rect(wr2, pants, (5, 11, 3, 5))
        pygame.draw.rect(wr2, pants, (8, 11, 3, 5))
        pygame.draw.rect(wr2, water_can, (12, 6, 3, 4))
        self.sprites['watering-right2'] = pygame.transform.scale(wr2, (16 * SCALE, 16 * SCALE))
    
    def load_bush(self):
        bush1_path = os.path.join('char', 'bush', 'bush1.png')
        bush2_path = os.path.join('char', 'bush', 'bush2.png')
        
        if os.path.exists(bush1_path) and os.path.exists(bush2_path):
            print(f"Loading bush sprites from char/bush/ folder...")
            self.bush1_sprite = pygame.image.load(bush1_path).convert_alpha()
            self.bush2_sprite = pygame.image.load(bush2_path).convert_alpha()
            self.bush1_sprite = pygame.transform.scale(self.bush1_sprite, (64, 64))
            self.bush2_sprite = pygame.transform.scale(self.bush2_sprite, (64, 64))
        else:
            print("Bush sprites not found, creating placeholders...")
            self.bush1_sprite = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.circle(self.bush1_sprite, (34, 139, 34), (32, 32), 30)
            pygame.draw.circle(self.bush1_sprite, (255, 0, 0), (25, 25), 5)
            pygame.draw.circle(self.bush1_sprite, (255, 0, 0), (40, 30), 5)
            
            self.bush2_sprite = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.circle(self.bush2_sprite, (34, 139, 34), (32, 32), 30)
    
    def load_fruit(self):
        fruit_path = os.path.join('char', 'fruit.png')
        
        if os.path.exists(fruit_path):
            print(f"Loading fruit from {fruit_path}...")
            self.fruit_sprite = pygame.image.load(fruit_path).convert_alpha()
            self.fruit_sprite = pygame.transform.scale(self.fruit_sprite, (32, 32))
        else:
            print("Fruit sprite not found, creating placeholder...")
            self.fruit_sprite = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(self.fruit_sprite, (255, 100, 100), (16, 16), 14)
            pygame.draw.circle(self.fruit_sprite, (255, 0, 0), (16, 16), 12)
    
    def load_trunk(self):
        trunk_path = os.path.join('char', 'trunk.png')
        
        if os.path.exists(trunk_path):
            print(f"Loading trunk from {trunk_path}...")
            self.trunk_sprite = pygame.image.load(trunk_path).convert_alpha()
            self.trunk_sprite = pygame.transform.scale(self.trunk_sprite, (64, 64))
        else:
            print("Trunk sprite not found, creating placeholder...")
            self.trunk_sprite = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.rect(self.trunk_sprite, (101, 67, 33), (5, 20, 54, 24))
            pygame.draw.ellipse(self.trunk_sprite, (139, 90, 43), (0, 18, 20, 28))
            pygame.draw.ellipse(self.trunk_sprite, (139, 90, 43), (44, 18, 20, 28))
        
        self.load_cutting_sprites()
    
    def load_cutting_sprites(self):
        sprite_folder = 'char'
        cutting_files = [
            'cut-behind1.png', 'cut-behind2.png',
            'cut-front1.png', 'cut-front2.png',
            'cut-left1.png', 'cut-left2.png',
            'cut-right1.png', 'cut-right2.png'
        ]
        
        sprite_paths = [os.path.join(sprite_folder, f) for f in cutting_files]
        all_exist = all(os.path.exists(p) for p in sprite_paths)
        
        if all_exist:
            print(f"Loading cutting sprites from {sprite_folder}/ folder...")
            for sprite_file, sprite_path in zip(cutting_files, sprite_paths):
                sprite_name = sprite_file.replace('.png', '')
                self.sprites[sprite_name] = pygame.image.load(sprite_path).convert_alpha()
                self.sprites[sprite_name] = pygame.transform.scale(
                    self.sprites[sprite_name], 
                    (16 * SCALE, 16 * SCALE)
                )
        else:
            print("Generating cutting sprites programmatically...")
            self.generate_cutting_sprites()
    
    def generate_cutting_sprites(self):
        sprite_size = 16
        
        skin = (255, 204, 153)
        shirt = (51, 102, 204)
        pants = (77, 51, 26)
        axe = (128, 128, 128)
        
        for i in range(1, 3):
            sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
            pygame.draw.rect(sprite, skin, (6, 2, 4, 4))
            pygame.draw.rect(sprite, shirt, (5, 6, 6, 5))
            pygame.draw.rect(sprite, pants, (5, 11, 3, 5))
            pygame.draw.rect(sprite, pants, (8, 11, 3, 5))
            offset = 1 if i == 2 else 0
            pygame.draw.rect(sprite, axe, (7 + offset, 0, 2, 4))
            self.sprites[f'cut-behind{i}'] = pygame.transform.scale(sprite, (16 * SCALE, 16 * SCALE))
        
        for i in range(1, 3):
            sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
            pygame.draw.rect(sprite, skin, (6, 2, 4, 4))
            pygame.draw.rect(sprite, shirt, (5, 6, 6, 5))
            pygame.draw.rect(sprite, pants, (5, 11, 3, 5))
            pygame.draw.rect(sprite, pants, (8, 11, 3, 5))
            offset = 1 if i == 2 else 0
            pygame.draw.rect(sprite, axe, (7 + offset, 12, 2, 4))
            self.sprites[f'cut-front{i}'] = pygame.transform.scale(sprite, (16 * SCALE, 16 * SCALE))
        
        for i in range(1, 3):
            sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
            pygame.draw.rect(sprite, skin, (6, 2, 4, 4))
            pygame.draw.rect(sprite, shirt, (5, 6, 6, 5))
            pygame.draw.rect(sprite, pants, (5, 11, 3, 5))
            pygame.draw.rect(sprite, pants, (8, 11, 3, 5))
            offset = 1 if i == 2 else 0
            pygame.draw.rect(sprite, axe, (1, 6 + offset, 4, 2))
            self.sprites[f'cut-left{i}'] = pygame.transform.scale(sprite, (16 * SCALE, 16 * SCALE))
        
        for i in range(1, 3):
            sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
            pygame.draw.rect(sprite, skin, (6, 2, 4, 4))
            pygame.draw.rect(sprite, shirt, (5, 6, 6, 5))
            pygame.draw.rect(sprite, pants, (5, 11, 3, 5))
            pygame.draw.rect(sprite, pants, (8, 11, 3, 5))
            offset = 1 if i == 2 else 0
            pygame.draw.rect(sprite, axe, (11, 6 + offset, 4, 2))
            self.sprites[f'cut-right{i}'] = pygame.transform.scale(sprite, (16 * SCALE, 16 * SCALE))
    
    def load_flower(self):
        flower_path = os.path.join('char', 'flower.png')
        
        if os.path.exists(flower_path):
            print(f"Loading flower from {flower_path}...")
            self.flower_sprite = pygame.image.load(flower_path).convert_alpha()
            self.flower_sprite = pygame.transform.scale(self.flower_sprite, (32, 64))
        else:
            print("Flower sprite not found, creating placeholder...")
            self.flower_sprite = pygame.Surface((32, 64), pygame.SRCALPHA)
            pygame.draw.rect(self.flower_sprite, (34, 139, 34), (14, 16, 4, 16))
            petal_color = (255, 105, 180)
            pygame.draw.circle(self.flower_sprite, petal_color, (16, 10), 6)
            pygame.draw.circle(self.flower_sprite, petal_color, (10, 13), 5)
            pygame.draw.circle(self.flower_sprite, petal_color, (22, 13), 5)
            pygame.draw.circle(self.flower_sprite, petal_color, (13, 18), 5)
            pygame.draw.circle(self.flower_sprite, petal_color, (19, 18), 5)
            pygame.draw.circle(self.flower_sprite, (255, 255, 0), (16, 14), 4)
    
    def load_mushroom(self):
        mushroom_path = os.path.join('char', 'mushroom.png')
        
        if os.path.exists(mushroom_path):
            print(f"Loading mushroom from {mushroom_path}...")
            self.mushroom_sprite = pygame.image.load(mushroom_path).convert_alpha()
            self.mushroom_sprite = pygame.transform.scale(self.mushroom_sprite, (32, 32))
        else:
            print("Mushroom sprite not found, creating placeholder...")
            self.mushroom_sprite = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.ellipse(self.mushroom_sprite, (200, 50, 50), (4, 4, 24, 16))
            pygame.draw.circle(self.mushroom_sprite, (255, 255, 255), (12, 10), 3)
            pygame.draw.circle(self.mushroom_sprite, (255, 255, 255), (20, 12), 2)
            pygame.draw.rect(self.mushroom_sprite, (240, 220, 180), (12, 16, 8, 12))
    
    def load_tree(self):
        tree_path = os.path.join('char', 'tree1.png')
        
        if os.path.exists(tree_path):
            print(f"Loading tree from {tree_path}...")
            self.tree_image = pygame.image.load(tree_path).convert_alpha()
            self.tree_sprite = pygame.transform.scale(self.tree_image, (128, 128))
        else:
            print("Tree image not found, creating placeholder...")
            self.tree_sprite = pygame.Surface((128, 128), pygame.SRCALPHA)
            pygame.draw.rect(self.tree_sprite, (101, 67, 33), (24, 40, 16, 24))
            pygame.draw.circle(self.tree_sprite, (34, 139, 34), (32, 24), 24)
            pygame.draw.circle(self.tree_sprite, (46, 125, 50), (32, 24), 20)
    
    def load_clock(self):
        clock_path = os.path.join('char', 'clock.png')
        
        if os.path.exists(clock_path):
            print(f"Loading clock from {clock_path}...")
            self.clock_image = pygame.image.load(clock_path).convert_alpha()
            self.clock_icon = pygame.transform.scale(self.clock_image, 
                                                     (CLOCK_ICON_SIZE, CLOCK_ICON_SIZE))
            clock_full_size = (CLOCK_DISPLAY_SIZE // 2 + 10) * 2
            self.clock_display = pygame.transform.scale(self.clock_image,
                                                       (clock_full_size, clock_full_size))
        else:
            print("Clock image not found, creating placeholder...")
            self.clock_icon = pygame.Surface((CLOCK_ICON_SIZE, CLOCK_ICON_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(self.clock_icon, GRAY, 
                             (CLOCK_ICON_SIZE//2, CLOCK_ICON_SIZE//2), 
                             CLOCK_ICON_SIZE//2 - 5)
            pygame.draw.circle(self.clock_icon, WHITE, 
                             (CLOCK_ICON_SIZE//2, CLOCK_ICON_SIZE//2), 
                             CLOCK_ICON_SIZE//2 - 10)
            
            clock_full_size = (CLOCK_DISPLAY_SIZE // 2 + 10) * 2
            self.clock_display = pygame.Surface((clock_full_size, clock_full_size), 
                                               pygame.SRCALPHA)
            pygame.draw.circle(self.clock_display, GRAY, 
                             (clock_full_size//2, clock_full_size//2), 
                             clock_full_size//2 - 5)
            pygame.draw.circle(self.clock_display, WHITE, 
                             (clock_full_size//2, clock_full_size//2), 
                             clock_full_size//2 - 10)
    
    def load_sounds(self):
        bgm_path = os.path.join('char', 'bgm.mp3')
        cut_path = os.path.join('char', 'cut.mp3')
        watering_path = os.path.join('char', 'watering.mp3')
        
        if os.path.exists(bgm_path):
            print(f"Loading background music from {bgm_path}...")
            pygame.mixer.music.load(bgm_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        else:
            print("Background music not found")
        
        if os.path.exists(cut_path):
            print(f"Loading cut sound from {cut_path}...")
            self.cut_sound = pygame.mixer.Sound(cut_path)
            self.cut_sound.set_volume(0.6)
        else:
            print("Cut sound not found")
            self.cut_sound = None
        
        if os.path.exists(watering_path):
            print(f"Loading watering sound from {watering_path}...")
            self.watering_sound = pygame.mixer.Sound(watering_path)
            self.watering_sound.set_volume(0.6)
        else:
            print("Watering sound not found")
            self.watering_sound = None
    
    def load_map(self):
        map_file = os.path.join('char', 'backyard.png')
        
        if os.path.exists(map_file):
            print(f"Loading map from {map_file}...")
            self.map_image = pygame.image.load(map_file).convert()
            self.map_width = self.map_image.get_width()
            self.map_height = self.map_image.get_height()
        elif os.path.exists('map.png'):
            print("Loading map from map.png...")
            self.map_image = pygame.image.load('map.png').convert()
            self.map_width = self.map_image.get_width()
            self.map_height = self.map_image.get_height()
        else:
            print("Creating default map (30x20 tiles)...")
            self.map_width = 30 * TILE_SIZE
            self.map_height = 20 * TILE_SIZE
            self.map_image = pygame.Surface((self.map_width, self.map_height))
            
            for y in range(0, self.map_height, TILE_SIZE):
                for x in range(0, self.map_width, TILE_SIZE):
                    if ((x // TILE_SIZE) + (y // TILE_SIZE)) % 2 == 0:
                        color = (51, 153, 51)
                    else:
                        color = (41, 143, 41)
                    pygame.draw.rect(self.map_image, color, (x, y, TILE_SIZE, TILE_SIZE))
            
            for i in range(20):
                pygame.draw.rect(self.map_image, BROWN, 
                                (3 * TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            
            house_color = (139, 115, 85)
            roof_color = (139, 69, 19)
            pygame.draw.rect(self.map_image, house_color, 
                           (10 * TILE_SIZE, 5 * TILE_SIZE, 8 * TILE_SIZE, 6 * TILE_SIZE))
            pygame.draw.rect(self.map_image, roof_color, 
                           (9 * TILE_SIZE, 4 * TILE_SIZE, 10 * TILE_SIZE, TILE_SIZE))
        
        self.map_surface = pygame.transform.scale(
            self.map_image,
            (self.map_width * SCALE, self.map_height * SCALE)
        )
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.clock_ui_active:
                        self.clock_ui_active = False
                    else:
                        self.running = False
                elif event.key == pygame.K_SPACE or event.key == pygame.K_e:
                    if not self.clock_ui_active and not self.watering and not self.picking and not self.cutting and not self.flower_watering and not self.mushroom_cutting:
                        if self.is_near_bush():
                            self.check_picking_action()
                        elif self.is_near_trunk():
                            self.check_cutting_action()
                        elif self.is_near_mushroom():
                            self.check_mushroom_cutting_action()
                        elif self.is_near_flower():
                            self.check_flower_watering_action()
                        else:
                            self.check_watering_action()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    self.handle_mouse_click(mouse_pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging_hand = None
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_hand:
                    mouse_pos = pygame.mouse.get_pos()
                    self.update_hand_angle(mouse_pos)
    
    def handle_mouse_click(self, pos):
        if self.all_missions_completed() and self.play_again_button_rect.collidepoint(pos):
            self.reset_game()
            return
        
        if self.clock_icon_rect.collidepoint(pos) and not self.clock_ui_active:
            self.clock_ui_active = True
            return
        
        if self.clock_ui_active:
            cx, cy = CLOCK_CENTER_X, CLOCK_CENTER_Y
            dx, dy = pos[0] - cx, pos[1] - cy
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < 30:
                self.clock_ui_active = False
                return
            
            if distance < CLOCK_DISPLAY_SIZE // 2 - 20:
                angle = math.degrees(math.atan2(dy, dx)) + 90
                if angle < 0:
                    angle += 360
                
                hour_diff = abs(self.angle_difference(angle, self.hour_angle))
                minute_diff = abs(self.angle_difference(angle, self.minute_angle))
                
                if hour_diff < 20:
                    self.dragging_hand = 'hour'
                elif minute_diff < 20:
                    self.dragging_hand = 'minute'
    
    def all_missions_completed(self):
        return all(mission['completed'] for mission in self.missions)
    
    def get_current_mission(self):
        for mission in self.missions:
            if not mission['completed']:
                return mission
        return None
    
    def can_do_mission_type(self, mission_title_keyword):
        current = self.get_current_mission()
        if current is None:
            return False
        return mission_title_keyword.lower() in current['title'].lower()
    
    def reset_game(self):
        self.player['x'] = 240
        self.player['y'] = 160
        self.player['direction'] = 'down'
        self.player['state'] = 'idle'
        
        self.camera_x = 0
        self.camera_y = 0
        
        self.hour_angle = 0
        self.minute_angle = 0
        self.clock_ui_active = False
        
        for bush in self.bushes:
            bush['picked'] = False
        
        for trunk in self.trunks:
            trunk['cut'] = False
        
        for flower in self.flowers:
            flower['watered'] = False
        
        for mushroom in self.mushrooms:
            mushroom['removed'] = False
        
        self.fruits_picked = 0
        self.trunks_cut = 0
        self.flowers_watered = 0
        self.mushrooms_removed = 0
        
        self.watering = False
        self.picking = False
        self.cutting = False
        self.flower_watering = False
        self.mushroom_cutting = False
        
        for mission in self.missions:
            mission['completed'] = False
        random.shuffle(self.missions)
        for i, mission in enumerate(self.missions, 1):
            mission['id'] = i
        
        self.notification_text = ""
        self.notification_timer = 0
        
        print("\n=== Game Restarted ===")
        print("Missions randomized!")
    
    def angle_difference(self, a1, a2):
        diff = a1 - a2
        while diff > 180:
            diff -= 360
        while diff < -180:
            diff += 360
        return diff
    
    def update_hand_angle(self, pos):
        cx, cy = CLOCK_CENTER_X, CLOCK_CENTER_Y
        dx, dy = pos[0] - cx, pos[1] - cy
        angle = math.degrees(math.atan2(dy, dx)) + 90
        if angle < 0:
            angle += 360
        
        if self.dragging_hand == 'hour':
            self.hour_angle = angle
        elif self.dragging_hand == 'minute':
            self.minute_angle = angle
    
    def is_clock_set_to_hour(self, hour):
        target_angle = (hour % 12) * 30
        angle_diff = abs(self.hour_angle - target_angle)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        return angle_diff <= 15
    
    def is_minute_at_12(self):
        angle_diff = min(abs(self.minute_angle - 0), abs(self.minute_angle - 360))
        return angle_diff <= 15
    
    def is_near_tree(self):
        player_x = self.player['x']
        player_y = self.player['y']
        
        for tree in self.trees:
            dx = tree['x'] - player_x
            dy = tree['y'] - player_y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < 70:
                return True
        return False
    
    def is_near_bush(self):
        player_x = self.player['x']
        player_y = self.player['y']
        
        for bush in self.bushes:
            if not bush['picked']:
                dx = bush['x'] - player_x
                dy = bush['y'] - player_y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance < 50:
                    return True
        return False
    
    def is_near_trunk(self):
        player_x = self.player['x']
        player_y = self.player['y']
        
        for trunk in self.trunks:
            if not trunk['cut']:
                dx = trunk['x'] - player_x
                dy = trunk['y'] - player_y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance < 50:
                    return True
        return False
    
    def is_near_flower(self):
        player_x = self.player['x']
        player_y = self.player['y']
        
        for flower in self.flowers:
            if not flower['watered']:
                dx = flower['x'] - player_x
                dy = flower['y'] - player_y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance < 40:
                    return True
        return False
    
    def is_near_mushroom(self):
        player_x = self.player['x']
        player_y = self.player['y']
        
        for mushroom in self.mushrooms:
            if not mushroom['removed']:
                dx = mushroom['x'] - player_x
                dy = mushroom['y'] - player_y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance < 40:
                    return True
        return False
    
    def check_trunk_collision(self, new_x, new_y):
        player_size = 12
        player_left = new_x
        player_right = new_x + player_size
        player_top = new_y
        player_bottom = new_y + player_size
        
        for trunk in self.trunks:
            if not trunk['cut']:
                trunk_size = 25
                trunk_left = trunk['x']
                trunk_right = trunk['x'] + trunk_size
                trunk_top = trunk['y']
                trunk_bottom = trunk['y'] + trunk_size
                
                if (player_right > trunk_left and player_left < trunk_right and
                    player_bottom > trunk_top and player_top < trunk_bottom):
                    return True
        return False
    
    def check_watering_action(self):
        if not self.can_do_mission_type('pohon'):
            print("Ini bukan misi yang aktif sekarang!")
            return
        
        mission = self.get_current_mission()
        if mission is None:
            return
        
        if not self.is_clock_set_to_hour(mission['required_hour']):
            print(f"Set jam ke {mission['required_hour']:02d}:00 terlebih dahulu!")
            return
        if not self.is_minute_at_12():
            print("Set jarum menit ke angka 12 terlebih dahulu!")
            return
        
        player_x = self.player['x']
        player_y = self.player['y']
        
        for tree in self.trees:
            dx = tree['x'] - player_x
            dy = tree['y'] - player_y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < 70:
                if dx < 0:
                    self.watering_side = 'left'
                else:
                    self.watering_side = 'right'
                
                self.watering = True
                self.watering_timer = 0
                
                if self.watering_sound:
                    self.watering_sound.play()
                
                if not mission['completed']:
                    mission['completed'] = True
                    self.notification_text = f"MISI SELESAI: {mission['title']}!"
                    self.notification_timer = 0
                    print(f"Misi selesai: {mission['title']}!")
                
                return
    
    def check_picking_action(self):
        if not self.can_do_mission_type('buah'):
            print("Ini bukan misi yang aktif sekarang!")
            return
        
        mission = self.get_current_mission()
        if mission is None:
            return
        
        if not self.is_clock_set_to_hour(mission['required_hour']):
            print(f"Set jam ke {mission['required_hour']:02d}:00 terlebih dahulu!")
            return
        if not self.is_minute_at_12():
            print("Set jarum menit ke angka 12 terlebih dahulu!")
            return
        
        player_x = self.player['x']
        player_y = self.player['y']
        
        for bush in self.bushes:
            if not bush['picked']:
                dx = bush['x'] - player_x
                dy = bush['y'] - player_y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance < 50:
                    bush['picked'] = True
                    self.picking = True
                    self.picking_timer = 0
                    self.fruits_picked += 1
                    
                    if self.fruits_picked >= 3:
                        if not mission['completed']:
                            mission['completed'] = True
                            self.notification_text = f"MISI SELESAI: {mission['title']}!"
                            self.notification_timer = 0
                            print(f"Misi selesai: {mission['title']}!")
                    
                    return
    
    def check_cutting_action(self):
        if not self.can_do_mission_type('kayu'):
            print("Ini bukan misi yang aktif sekarang!")
            return
        
        mission = self.get_current_mission()
        if mission is None:
            return
        
        if not self.is_clock_set_to_hour(mission['required_hour']):
            print(f"Set jam ke {mission['required_hour']:02d}:00 terlebih dahulu!")
            return
        if not self.is_minute_at_12():
            print("Set jarum menit ke angka 12 terlebih dahulu!")
            return
        
        player_x = self.player['x']
        player_y = self.player['y']
        
        for trunk in self.trunks:
            if not trunk['cut']:
                dx = trunk['x'] - player_x
                dy = trunk['y'] - player_y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance < 50:
                    if abs(dx) > abs(dy):
                        if dx < 0:
                            self.cutting_side = 'left'
                        else:
                            self.cutting_side = 'right'
                    else:
                        if dy < 0:
                            self.cutting_side = 'behind'
                        else:
                            self.cutting_side = 'front'
                    
                    trunk['cut'] = True
                    
                    if self.cut_sound:
                        self.cut_sound.play()
                    
                    self.cutting = True
                    self.cutting_timer = 0
                    self.trunks_cut += 1
                    
                    if self.trunks_cut >= 2:
                        if not mission['completed']:
                            mission['completed'] = True
                            self.notification_text = f"MISI SELESAI: {mission['title']}!"
                            self.notification_timer = 0
                            print(f"Misi selesai: {mission['title']}!")
                    
                    return
    
    def check_flower_watering_action(self):
        if not self.can_do_mission_type('bunga'):
            print("Ini bukan misi yang aktif sekarang!")
            return
        
        mission = self.get_current_mission()
        if mission is None:
            return
        
        if not self.is_clock_set_to_hour(mission['required_hour']):
            print(f"Set jam ke {mission['required_hour']:02d}:00 terlebih dahulu!")
            return
        
        player_x = self.player['x']
        player_y = self.player['y']
        
        for flower in self.flowers:
            if not flower['watered']:
                dx = flower['x'] - player_x
                dy = flower['y'] - player_y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance < 40:
                    if dx < 0:
                        self.flower_watering_side = 'left'
                    else:
                        self.flower_watering_side = 'right'
                    
                    flower['watered'] = True
                    
                    if self.watering_sound:
                        self.watering_sound.play()
                    
                    self.flower_watering = True
                    self.flower_watering_timer = 0
                    self.flowers_watered += 1
                    
                    if self.flowers_watered >= 1:
                        if not mission['completed']:
                            mission['completed'] = True
                            self.notification_text = f"MISI SELESAI: {mission['title']}!"
                            self.notification_timer = 0
                            print(f"Misi selesai: {mission['title']}!")
                    
                    return
    
    def check_mushroom_cutting_action(self):
        if not self.can_do_mission_type('jamur'):
            print("Ini bukan misi yang aktif sekarang!")
            return
        
        mission = self.get_current_mission()
        if mission is None:
            return
        
        if not self.is_clock_set_to_hour(mission['required_hour']):
            print(f"Set jam ke {mission['required_hour']:02d}:00 terlebih dahulu!")
            return
        
        player_x = self.player['x']
        player_y = self.player['y']
        
        for mushroom in self.mushrooms:
            if not mushroom['removed']:
                dx = mushroom['x'] - player_x
                dy = mushroom['y'] - player_y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance < 40:
                    if abs(dx) > abs(dy):
                        if dx < 0:
                            self.mushroom_cutting_side = 'left'
                        else:
                            self.mushroom_cutting_side = 'right'
                    else:
                        if dy < 0:
                            self.mushroom_cutting_side = 'behind'
                        else:
                            self.mushroom_cutting_side = 'front'
                    
                    mushroom['removed'] = True
                    
                    if self.cut_sound:
                        self.cut_sound.play()
                    
                    self.mushroom_cutting = True
                    self.mushroom_cutting_timer = 0
                    self.mushrooms_removed += 1
                    
                    if self.mushrooms_removed >= len(self.mushrooms):
                        if not mission['completed']:
                            mission['completed'] = True
                            self.notification_text = f"MISI SELESAI: {mission['title']}!"
                            self.notification_timer = 0
                            print(f"Misi selesai: {mission['title']}!")
                    
                    return
    
    def update(self, dt):
        if self.notification_timer < self.notification_duration:
            self.notification_timer += dt
        
        if self.mushroom_cutting:
            self.mushroom_cutting_timer += dt
            if self.mushroom_cutting_timer >= self.mushroom_cutting_duration:
                self.mushroom_cutting = False
                self.mushroom_cutting_timer = 0
            self.player['animation_timer'] += dt
            if self.player['animation_timer'] >= self.animation_speed:
                self.player['animation_timer'] = 0
                self.player['animation_frame'] = (self.player['animation_frame'] + 1) % 2
            return
        
        if self.flower_watering:
            self.flower_watering_timer += dt
            if self.flower_watering_timer >= self.flower_watering_duration:
                self.flower_watering = False
                self.flower_watering_timer = 0
            self.player['animation_timer'] += dt
            if self.player['animation_timer'] >= self.animation_speed:
                self.player['animation_timer'] = 0
                self.player['animation_frame'] = (self.player['animation_frame'] + 1) % 2
            return
        
        if self.picking:
            self.picking_timer += dt
            if self.picking_timer >= self.picking_duration:
                self.picking = False
                self.picking_timer = 0
        
        if self.cutting:
            self.cutting_timer += dt
            if self.cutting_timer >= self.cutting_duration:
                self.cutting = False
                self.cutting_timer = 0
            self.player['animation_timer'] += dt
            if self.player['animation_timer'] >= self.animation_speed:
                self.player['animation_timer'] = 0
                self.player['animation_frame'] = (self.player['animation_frame'] + 1) % 2
            return
        
        if self.watering:
            self.watering_timer += dt
            if self.watering_timer >= self.watering_duration:
                self.watering = False
                self.watering_timer = 0
            self.player['animation_timer'] += dt
            if self.player['animation_timer'] >= self.animation_speed:
                self.player['animation_timer'] = 0
                self.player['animation_frame'] = (self.player['animation_frame'] + 1) % 2
            return
        
        if not self.clock_ui_active:
            keys = pygame.key.get_pressed()
            moving = False
            dx, dy = 0, 0
            
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = self.player['speed'] * dt
                self.player['direction'] = 'right'
                moving = True
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -self.player['speed'] * dt
                self.player['direction'] = 'left'
                moving = True
            
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = self.player['speed'] * dt
                self.player['direction'] = 'down'
                moving = True
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -self.player['speed'] * dt
                self.player['direction'] = 'up'
                moving = True
            
            if moving:
                new_x = self.player['x'] + dx
                new_y = self.player['y'] + dy
                
                if not self.check_trunk_collision(new_x, new_y):
                    self.player['x'] = new_x
                    self.player['y'] = new_y
                    self.player['state'] = 'walking'
                else:
                    if dx != 0 and not self.check_trunk_collision(self.player['x'] + dx, self.player['y']):
                        self.player['x'] += dx
                        self.player['state'] = 'walking'
                    elif dy != 0 and not self.check_trunk_collision(self.player['x'], self.player['y'] + dy):
                        self.player['y'] += dy
                        self.player['state'] = 'walking'
                    else:
                        self.player['state'] = 'idle'
            else:
                self.player['state'] = 'idle'
            
            self.player['x'] = max(0, min(self.player['x'], 
                                         self.map_width - self.player['width']))
            self.player['y'] = max(0, min(self.player['y'], 
                                         self.map_height - self.player['height']))
            
            self.player['animation_timer'] += dt
            if self.player['animation_timer'] >= self.animation_speed:
                self.player['animation_timer'] = 0
                self.player['animation_frame'] = (self.player['animation_frame'] + 1) % 2
            
            self.camera_x = self.player['x'] - (SCREEN_WIDTH // (2 * SCALE)) + self.player['width'] // 2
            self.camera_y = self.player['y'] - (SCREEN_HEIGHT // (2 * SCALE)) + self.player['height'] // 2
            
            self.camera_x = max(0, min(self.camera_x, self.map_width - SCREEN_WIDTH // SCALE))
            self.camera_y = max(0, min(self.camera_y, self.map_height - SCREEN_HEIGHT // SCALE))
    
    def draw(self):
        self.screen.fill(BLACK)
        
        map_x = -self.camera_x * SCALE
        map_y = -self.camera_y * SCALE
        self.screen.blit(self.map_surface, (map_x, map_y))
        
        state = self.player['state']
        direction = self.player['direction']
        frame = self.player['animation_frame'] + 1
        
        dir_map = {'down': 'front', 'up': 'back', 'left': 'left', 'right': 'right'}
        sprite_dir = dir_map.get(direction, 'front')
        
        if state == 'idle':
            sprite_key = f'idle-{sprite_dir}{frame}'
        else:
            sprite_key = f'walk-{sprite_dir}{frame}'
        
        player_screen_x = (self.player['x'] - self.camera_x) * SCALE
        player_screen_y = (self.player['y'] - self.camera_y) * SCALE
        
        if self.mushroom_cutting:
            frame = self.player['animation_frame'] + 1
            sprite_key = f'cut-{self.mushroom_cutting_side}{frame}'
        elif self.flower_watering:
            frame = self.player['animation_frame'] + 1
            sprite_key = f'watering-{self.flower_watering_side}{frame}'
        elif self.watering:
            frame = self.player['animation_frame'] + 1
            sprite_key = f'watering-{self.watering_side}{frame}'
        elif self.cutting:
            frame = self.player['animation_frame'] + 1
            sprite_key = f'cut-{self.cutting_side}{frame}'
        
        entities = []
        
        entities.append({
            'type': 'player',
            'y': self.player['y'] + 16,
            'sprite': self.sprites[sprite_key],
            'x': player_screen_x,
            'screen_y': player_screen_y
        })
        
        for tree in self.trees:
            entities.append({
                'type': 'tree',
                'y': tree['y'] + 64,
                'sprite': self.tree_sprite,
                'x': (tree['x'] - self.camera_x) * SCALE,
                'screen_y': (tree['y'] - self.camera_y) * SCALE
            })
        
        for trunk in self.trunks:
            if not trunk['cut']:
                entities.append({
                    'type': 'trunk',
                    'y': trunk['y'] + 32,
                    'sprite': self.trunk_sprite,
                    'x': (trunk['x'] - self.camera_x) * SCALE,
                    'screen_y': (trunk['y'] - self.camera_y) * SCALE
                })
        
        for bush in self.bushes:
            bush_sprite = self.bush2_sprite if bush['picked'] else self.bush1_sprite
            entities.append({
                'type': 'bush',
                'y': bush['y'] + 32,
                'sprite': bush_sprite,
                'x': (bush['x'] - self.camera_x) * SCALE,
                'screen_y': (bush['y'] - self.camera_y) * SCALE
            })
        
        for flower in self.flowers:
            entities.append({
                'type': 'flower',
                'y': flower['y'] + 16,
                'sprite': self.flower_sprite,
                'x': (flower['x'] - self.camera_x) * SCALE,
                'screen_y': (flower['y'] - self.camera_y) * SCALE
            })
        
        for mushroom in self.mushrooms:
            if not mushroom['removed']:
                entities.append({
                    'type': 'mushroom',
                    'y': mushroom['y'] + 16,
                    'sprite': self.mushroom_sprite,
                    'x': (mushroom['x'] - self.camera_x) * SCALE,
                    'screen_y': (mushroom['y'] - self.camera_y) * SCALE
                })
        
        entities.sort(key=lambda e: e['y'])
        
        for entity in entities:
            self.screen.blit(entity['sprite'], (entity['x'], entity['screen_y']))
        
        if self.picking:
            fruit_x = player_screen_x + 8
            fruit_y = player_screen_y - 40
            self.screen.blit(self.fruit_sprite, (fruit_x, fruit_y))
        
        self.screen.blit(self.clock_icon, (10, 10))
        
        self.draw_mission_box()
        
        if self.clock_ui_active:
            self.draw_clock_ui()
        
        self.draw_watering_prompt()
        
        self.draw_notification()
        
        pygame.display.flip()
    
    def draw_mission_box(self):
        current_mission = None
        for mission in self.missions:
            if not mission['completed']:
                current_mission = mission
                break
        
        if current_mission is None:
            mission_bg = pygame.Surface((300, 120))
            mission_bg.set_alpha(200)
            mission_bg.fill((40, 40, 60))
            self.screen.blit(mission_bg, (150, 10))
            
            pygame.draw.rect(self.screen, (0, 255, 0), (150, 10, 300, 120), 2)
            
            font_title = pygame.font.Font(None, 32)
            title_surface = font_title.render("SEMUA MISI SELESAI!", True, (0, 255, 0))
            title_rect = title_surface.get_rect(center=(300, 50))
            self.screen.blit(title_surface, title_rect)
            
            font_subtitle = pygame.font.Font(None, 24)
            subtitle_surface = font_subtitle.render("Udah paham materinya?", True, (255, 215, 0))
            subtitle_rect = subtitle_surface.get_rect(center=(300, 85))
            self.screen.blit(subtitle_surface, subtitle_rect)
            
            mouse_pos = pygame.mouse.get_pos()
            button_color = (100, 200, 100) if self.play_again_button_rect.collidepoint(mouse_pos) else (50, 150, 50)
            pygame.draw.rect(self.screen, button_color, self.play_again_button_rect)
            pygame.draw.rect(self.screen, WHITE, self.play_again_button_rect, 3)
            
            button_font = pygame.font.Font(None, 36)
            button_text = button_font.render("Main Lagi", True, WHITE)
            button_text_rect = button_text.get_rect(center=self.play_again_button_rect.center)
            self.screen.blit(button_text, button_text_rect)
            
            return
        
        mission_bg = pygame.Surface((300, 140))
        mission_bg.set_alpha(200)
        mission_bg.fill((40, 40, 60))
        self.screen.blit(mission_bg, (150, 10))
        
        pygame.draw.rect(self.screen, WHITE, (150, 10, 300, 140), 2)
        
        font_title = pygame.font.Font(None, 28)
        title_text = f"MISI {current_mission['id']}/5"
        title_surface = font_title.render(title_text, True, (255, 215, 0))
        self.screen.blit(title_surface, (160, 20))
        
        font_mission = pygame.font.Font(None, 24)
        mission_surface = font_mission.render(current_mission['title'], True, WHITE)
        self.screen.blit(mission_surface, (160, 55))
        
        font_desc = pygame.font.Font(None, 20)
        desc_surface = font_desc.render(current_mission['description'], True, (180, 180, 180))
        self.screen.blit(desc_surface, (160, 85))
        
        completed_count = sum(1 for m in self.missions if m['completed'])
        progress_text = f"Selesai: {completed_count}/5"
        progress_surface = font_desc.render(progress_text, True, (100, 200, 100))
        self.screen.blit(progress_surface, (160, 115))
    
    def draw_notification(self):
        if self.notification_timer < self.notification_duration and self.notification_text:
            font = pygame.font.Font(None, 36)
            text_surface = font.render(self.notification_text, True, (0, 255, 0))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
            
            bg_rect = text_rect.inflate(40, 20)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.set_alpha(200)
            bg_surface.fill((20, 20, 40))
            self.screen.blit(bg_surface, bg_rect.topleft)
            
            pygame.draw.rect(self.screen, (0, 255, 0), bg_rect, 3)
            
            self.screen.blit(text_surface, text_rect)
    
    def draw_watering_prompt(self):
        if not self.watering and not self.picking and not self.cutting and not self.flower_watering and not self.mushroom_cutting and not self.clock_ui_active:
            text = None
            
            if self.is_near_bush():
                text = "Tekan E untuk memetik buah"
            elif self.is_near_trunk():
                text = "Tekan E untuk singkirkan kayu"
            elif self.is_near_mushroom():
                text = "Tekan E untuk singkirkan jamur"
            elif self.is_near_flower():
                text = "Tekan E untuk menyiram bunga"
            elif self.is_near_tree():
                text = "Tekan E untuk menyiram pohon"
            
            if text:
                font = pygame.font.Font(None, 28)
                text_surface = font.render(text, True, WHITE)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
                
                bg_rect = text_rect.inflate(30, 15)
                bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
                bg_surface.set_alpha(180)
                bg_surface.fill((40, 40, 60))
                self.screen.blit(bg_surface, bg_rect.topleft)
                
                pygame.draw.rect(self.screen, (100, 150, 255), bg_rect, 2)
                
                self.screen.blit(text_surface, text_rect)
    
    def draw_clock_ui(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        cx, cy = CLOCK_CENTER_X, CLOCK_CENTER_Y
        clock_radius = CLOCK_DISPLAY_SIZE // 2 + 10
        
        clock_full_size = clock_radius * 2
        clock_x = cx - clock_radius
        clock_y = cy - clock_radius
        self.screen.blit(self.clock_display, (clock_x, clock_y))
        
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            outer_radius = CLOCK_DISPLAY_SIZE // 2 - 20
            inner_radius = outer_radius - 15
            
            x1 = cx + math.cos(angle) * inner_radius
            y1 = cy + math.sin(angle) * inner_radius
            x2 = cx + math.cos(angle) * outer_radius
            y2 = cy + math.sin(angle) * outer_radius
            
            pygame.draw.line(self.screen, BLACK, (x1, y1), (x2, y2), 3)
        
        minute_angle_rad = math.radians(self.minute_angle - 90)
        minute_length = CLOCK_DISPLAY_SIZE // 2 - 250
        minute_x = cx + math.cos(minute_angle_rad) * minute_length
        minute_y = cy + math.sin(minute_angle_rad) * minute_length
        pygame.draw.line(self.screen, DARK_BLUE, (cx, cy), (minute_x, minute_y), 4)
        
        hour_angle_rad = math.radians(self.hour_angle - 90)
        hour_length = CLOCK_DISPLAY_SIZE // 2 - 320
        hour_x = cx + math.cos(hour_angle_rad) * hour_length
        hour_y = cy + math.sin(hour_angle_rad) * hour_length
        pygame.draw.line(self.screen, RED, (cx, cy), (hour_x, hour_y), 6)
        
        pygame.draw.circle(self.screen, BLACK, (cx, cy), 12)
        pygame.draw.circle(self.screen, WHITE, (cx, cy), 8)
        
        font = pygame.font.Font(None, 28)
        instructions = [
            "Klik dan drag jarum untuk mengubah waktu",
            "Klik pusat jam atau tekan ESC untuk keluar"
        ]
        y_offset = cy + CLOCK_DISPLAY_SIZE // 2 + 30
        for text in instructions:
            surface = font.render(text, True, WHITE)
            text_rect = surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(surface, text_rect)
            y_offset += 35
    
    def run(self):
        print("\n=== Game Started ===")
        print("Controls:")
        print("  Arrow Keys atau WASD - Move")
        print("  SPASI atau E - Water tree (when near)")
        print("  Click Clock Icon - Buka UI jam")
        print("  Drag Clock Hands - Set Waktu")
        print("  ESC - Close Clock / Quit")
        print("========================\n")
        
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()
