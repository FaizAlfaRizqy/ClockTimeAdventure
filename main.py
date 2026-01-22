"""
Classic 2D RPG Game - Python Pygame Version
Map menggunakan file PNG, sprite menggunakan idle1.png, idle2.png, walk1.png, walk2.png
Rencana Misi:
Singkirkan kayu yang menghalangi jalan
petik buah
siram bunga
singkirkan semua jamur
"""

import pygame
import sys
import os
import math
from pathlib import Path

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 16
SCALE = 2
FPS = 60

# Clock constants
CLOCK_ICON_SIZE = 128
CLOCK_DISPLAY_SIZE = 800
CLOCK_CENTER_X = SCREEN_WIDTH // 2
CLOCK_CENTER_Y = SCREEN_HEIGHT // 2

# Colors
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
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Little Cat Time Adventure - Faiz")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Load or create assets
        self.load_sprites()
        self.load_map()
        self.load_clock()
        
        # Player
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
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
        # Animation
        self.animation_speed = 0.3
        
        # Clock state
        self.clock_ui_active = False
        self.hour_angle = 0  # 0 degrees = 12 o'clock
        self.minute_angle = 0
        self.dragging_hand = None  # 'hour', 'minute', or None
        self.clock_icon_rect = pygame.Rect(10, 10, CLOCK_ICON_SIZE, CLOCK_ICON_SIZE)
        
        # Trees
        self.trees = [
            {'x': 2, 'y': 50},
            {'x': 100, 'y': 230},
            {'x': 350, 'y': 150},
            {'x': 350, 'y': 250},
        ]
        self.load_tree()
        
        # Bushes for fruit picking
        self.bushes = [
            {'x': 220, 'y': 270, 'picked': False},
            {'x': 280, 'y': 270, 'picked': False},
            {'x': 250, 'y': 270, 'picked': False},
        ]
        self.load_bush()
        self.load_fruit()
        
        # Trunks for cutting
        self.trunks = [
            {'x': 400, 'y': 100, 'cut': False},
            {'x': 50, 'y': 150, 'cut': False},
        ]
        self.load_trunk()
        
        # Watering state
        self.watering = False
        self.watering_side = None  # 'left' or 'right'
        self.watering_timer = 0
        self.watering_duration = 1.0  # seconds
        
        # Picking state
        self.picking = False
        self.picking_timer = 0
        self.picking_duration = 3.0  # seconds to show fruit
        self.fruits_picked = 0
        
        # Cutting state
        self.cutting = False
        self.cutting_side = None  # 'behind', 'front', 'left', 'right'
        self.cutting_timer = 0
        self.cutting_duration = 1.5  # seconds
        self.trunks_cut = 0
        
        # Missions
        self.missions = [
            {
                'id': 1,
                'title': 'Siram pohon pada jam 1',
                'description': 'Set jam ke 01:00 lalu siram pohon',
                'completed': False,
                'required_hour': 1  # 1 o'clock = 30 degrees
            },
            {
                'id': 2,
                'title': 'Petik 3 buah dari semak',
                'description': 'Set jam ke 03:00 lalu petik buah',
                'completed': False,
                'required_hour': 3  # 3 o'clock = 90 degrees
            },
            {
                'id': 3,
                'title': 'Singkirkan 2 batang kayu',
                'description': 'Set jam ke 05:00 lalu singkirkan kayu',
                'completed': False,
                'required_hour': 5  # 5 o'clock = 150 degrees
            }
        ]
        self.mission_box_rect = pygame.Rect(150, 10, 300, 200)
        
        # Notification system
        self.notification_text = ""
        self.notification_timer = 0
        self.notification_duration = 3.0  # seconds
        
    def load_sprites(self):
        """Load or generate player sprites"""
        self.sprites = {}
        sprite_folder = 'char'
        sprite_files = ['idle1.png', 'idle2.png', 'walk1.png', 'walk2.png']
        
        # Check if sprites exist in char folder
        sprite_paths = [os.path.join(sprite_folder, f) for f in sprite_files]
        all_exist = all(os.path.exists(p) for p in sprite_paths)
        
        if all_exist:
            print(f"Loading sprites from {sprite_folder}/ folder...")
            for sprite_file, sprite_path in zip(sprite_files, sprite_paths):
                sprite_name = sprite_file.replace('.png', '')
                self.sprites[sprite_name] = pygame.image.load(sprite_path).convert_alpha()
        else:
            # Try loading from current directory
            all_exist_current = all(os.path.exists(f) for f in sprite_files)
            if all_exist_current:
                print("Loading sprites from current directory...")
                for sprite_file in sprite_files:
                    sprite_name = sprite_file.replace('.png', '')
                    self.sprites[sprite_name] = pygame.image.load(sprite_file).convert_alpha()
            else:
                print("Generating sprites programmatically...")
                self.generate_sprites()
        
        # Scale sprites
        for key in self.sprites:
            self.sprites[key] = pygame.transform.scale(
                self.sprites[key], 
                (16 * SCALE, 16 * SCALE)
            )
        
        # Load watering sprites
        self.load_watering_sprites()
    
    def generate_sprites(self):
        """Generate simple placeholder sprites"""
        sprite_size = 16
        
        # Color definitions
        skin = (255, 204, 153)
        shirt = (51, 102, 204)
        pants = (77, 51, 26)
        
        # Create idle1
        idle1 = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        pygame.draw.rect(idle1, skin, (6, 2, 4, 4))  # Head
        pygame.draw.rect(idle1, shirt, (5, 6, 6, 5))  # Body
        pygame.draw.rect(idle1, pants, (5, 11, 3, 5))  # Left leg
        pygame.draw.rect(idle1, pants, (8, 11, 3, 5))  # Right leg
        self.sprites['idle1'] = idle1
        
        # Create idle2 (slightly different)
        idle2 = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        pygame.draw.rect(idle2, skin, (6, 2, 4, 4))
        pygame.draw.rect(idle2, shirt, (5, 6, 6, 5))
        pygame.draw.rect(idle2, pants, (5, 11, 3, 5))
        pygame.draw.rect(idle2, pants, (8, 11, 3, 5))
        self.sprites['idle2'] = idle2
        
        # Create walk1
        walk1 = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        pygame.draw.rect(walk1, skin, (6, 2, 4, 4))
        pygame.draw.rect(walk1, shirt, (5, 6, 6, 5))
        pygame.draw.rect(walk1, pants, (4, 11, 3, 5))  # Left leg forward
        pygame.draw.rect(walk1, pants, (9, 12, 3, 4))  # Right leg back
        self.sprites['walk1'] = walk1
        
        # Create walk2
        walk2 = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        pygame.draw.rect(walk2, skin, (6, 2, 4, 4))
        pygame.draw.rect(walk2, shirt, (5, 6, 6, 5))
        pygame.draw.rect(walk2, pants, (9, 11, 3, 5))  # Right leg forward
        pygame.draw.rect(walk2, pants, (4, 12, 3, 4))  # Left leg back
        self.sprites['walk2'] = walk2
    
    def load_watering_sprites(self):
        """Load watering sprites"""
        sprite_folder = 'char'
        watering_files = ['watering-left1.png', 'watering-left2.png', 
                         'watering-right1.png', 'watering-right2.png']
        
        # Check if sprites exist
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
        """Generate simple placeholder watering sprites"""
        sprite_size = 16
        
        # Color definitions
        skin = (255, 204, 153)
        shirt = (51, 102, 204)
        pants = (77, 51, 26)
        water_can = (150, 150, 150)
        
        # Create watering-left1
        wl1 = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        pygame.draw.rect(wl1, skin, (6, 2, 4, 4))  # Head
        pygame.draw.rect(wl1, shirt, (5, 6, 6, 5))  # Body
        pygame.draw.rect(wl1, pants, (5, 11, 3, 5))  # Legs
        pygame.draw.rect(wl1, pants, (8, 11, 3, 5))
        pygame.draw.rect(wl1, water_can, (2, 5, 3, 4))  # Water can on left
        self.sprites['watering-left1'] = pygame.transform.scale(wl1, (16 * SCALE, 16 * SCALE))
        
        # Create watering-left2
        wl2 = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        pygame.draw.rect(wl2, skin, (6, 2, 4, 4))
        pygame.draw.rect(wl2, shirt, (5, 6, 6, 5))
        pygame.draw.rect(wl2, pants, (5, 11, 3, 5))
        pygame.draw.rect(wl2, pants, (8, 11, 3, 5))
        pygame.draw.rect(wl2, water_can, (1, 6, 3, 4))  # Water can slightly lower
        self.sprites['watering-left2'] = pygame.transform.scale(wl2, (16 * SCALE, 16 * SCALE))
        
        # Create watering-right1
        wr1 = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        pygame.draw.rect(wr1, skin, (6, 2, 4, 4))  # Head
        pygame.draw.rect(wr1, shirt, (5, 6, 6, 5))  # Body
        pygame.draw.rect(wr1, pants, (5, 11, 3, 5))  # Legs
        pygame.draw.rect(wr1, pants, (8, 11, 3, 5))
        pygame.draw.rect(wr1, water_can, (11, 5, 3, 4))  # Water can on right
        self.sprites['watering-right1'] = pygame.transform.scale(wr1, (16 * SCALE, 16 * SCALE))
        
        # Create watering-right2
        wr2 = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        pygame.draw.rect(wr2, skin, (6, 2, 4, 4))
        pygame.draw.rect(wr2, shirt, (5, 6, 6, 5))
        pygame.draw.rect(wr2, pants, (5, 11, 3, 5))
        pygame.draw.rect(wr2, pants, (8, 11, 3, 5))
        pygame.draw.rect(wr2, water_can, (12, 6, 3, 4))  # Water can slightly lower
        self.sprites['watering-right2'] = pygame.transform.scale(wr2, (16 * SCALE, 16 * SCALE))
    
    def load_bush(self):
        """Load bush sprites"""
        bush1_path = os.path.join('char', 'bush', 'bush1.png')
        bush2_path = os.path.join('char', 'bush', 'bush2.png')
        
        if os.path.exists(bush1_path) and os.path.exists(bush2_path):
            print(f"Loading bush sprites from char/bush/ folder...")
            self.bush1_sprite = pygame.image.load(bush1_path).convert_alpha()
            self.bush2_sprite = pygame.image.load(bush2_path).convert_alpha()
            # Scale to 64x64
            self.bush1_sprite = pygame.transform.scale(self.bush1_sprite, (64, 64))
            self.bush2_sprite = pygame.transform.scale(self.bush2_sprite, (64, 64))
        else:
            print("Bush sprites not found, creating placeholders...")
            # Create placeholder bushes
            self.bush1_sprite = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.circle(self.bush1_sprite, (34, 139, 34), (32, 32), 30)
            pygame.draw.circle(self.bush1_sprite, (255, 0, 0), (25, 25), 5)  # Red berry
            pygame.draw.circle(self.bush1_sprite, (255, 0, 0), (40, 30), 5)  # Red berry
            
            self.bush2_sprite = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.circle(self.bush2_sprite, (34, 139, 34), (32, 32), 30)
    
    def load_fruit(self):
        """Load fruit sprite"""
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
        """Load trunk sprite"""
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
        
        # Load cutting sprites
        self.load_cutting_sprites()
    
    def load_cutting_sprites(self):
        """Load cutting sprites for different directions"""
        sprite_folder = 'char'
        cutting_files = [
            'cut-behind1.png', 'cut-behind2.png',
            'cut-front1.png', 'cut-front2.png',
            'cut-left1.png', 'cut-left2.png',
            'cut-right1.png', 'cut-right2.png'
        ]
        
        # Check if sprites exist
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
        """Generate simple placeholder cutting sprites"""
        sprite_size = 16
        
        # Color definitions
        skin = (255, 204, 153)
        shirt = (51, 102, 204)
        pants = (77, 51, 26)
        axe = (128, 128, 128)
        
        # Behind position (cutting above)
        for i in range(1, 3):
            sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
            pygame.draw.rect(sprite, skin, (6, 2, 4, 4))  # Head
            pygame.draw.rect(sprite, shirt, (5, 6, 6, 5))  # Body
            pygame.draw.rect(sprite, pants, (5, 11, 3, 5))  # Legs
            pygame.draw.rect(sprite, pants, (8, 11, 3, 5))
            # Axe above head
            offset = 1 if i == 2 else 0
            pygame.draw.rect(sprite, axe, (7 + offset, 0, 2, 4))
            self.sprites[f'cut-behind{i}'] = pygame.transform.scale(sprite, (16 * SCALE, 16 * SCALE))
        
        # Front position (cutting below)
        for i in range(1, 3):
            sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
            pygame.draw.rect(sprite, skin, (6, 2, 4, 4))  # Head
            pygame.draw.rect(sprite, shirt, (5, 6, 6, 5))  # Body
            pygame.draw.rect(sprite, pants, (5, 11, 3, 5))  # Legs
            pygame.draw.rect(sprite, pants, (8, 11, 3, 5))
            # Axe below
            offset = 1 if i == 2 else 0
            pygame.draw.rect(sprite, axe, (7 + offset, 12, 2, 4))
            self.sprites[f'cut-front{i}'] = pygame.transform.scale(sprite, (16 * SCALE, 16 * SCALE))
        
        # Left position
        for i in range(1, 3):
            sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
            pygame.draw.rect(sprite, skin, (6, 2, 4, 4))  # Head
            pygame.draw.rect(sprite, shirt, (5, 6, 6, 5))  # Body
            pygame.draw.rect(sprite, pants, (5, 11, 3, 5))  # Legs
            pygame.draw.rect(sprite, pants, (8, 11, 3, 5))
            # Axe on left
            offset = 1 if i == 2 else 0
            pygame.draw.rect(sprite, axe, (1, 6 + offset, 4, 2))
            self.sprites[f'cut-left{i}'] = pygame.transform.scale(sprite, (16 * SCALE, 16 * SCALE))
        
        # Right position
        for i in range(1, 3):
            sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
            pygame.draw.rect(sprite, skin, (6, 2, 4, 4))  # Head
            pygame.draw.rect(sprite, shirt, (5, 6, 6, 5))  # Body
            pygame.draw.rect(sprite, pants, (5, 11, 3, 5))  # Legs
            pygame.draw.rect(sprite, pants, (8, 11, 3, 5))
            # Axe on right
            offset = 1 if i == 2 else 0
            pygame.draw.rect(sprite, axe, (11, 6 + offset, 4, 2))
            self.sprites[f'cut-right{i}'] = pygame.transform.scale(sprite, (16 * SCALE, 16 * SCALE))
    
    def load_tree(self):
        """Load tree sprite"""
        tree_path = os.path.join('char', 'tree1.png')
        
        if os.path.exists(tree_path):
            print(f"Loading tree from {tree_path}...")
            self.tree_image = pygame.image.load(tree_path).convert_alpha()
            # Scale tree to 128x128 pixels
            self.tree_sprite = pygame.transform.scale(self.tree_image, (128, 128))
        else:
            print("Tree image not found, creating placeholder...")
            # Create simple placeholder tree (128x128)
            self.tree_sprite = pygame.Surface((128, 128), pygame.SRCALPHA)
            # Tree trunk
            pygame.draw.rect(self.tree_sprite, (101, 67, 33), (24, 40, 16, 24))
            # Tree leaves (green circle)
            pygame.draw.circle(self.tree_sprite, (34, 139, 34), (32, 24), 24)
            pygame.draw.circle(self.tree_sprite, (46, 125, 50), (32, 24), 20)
    
    def load_clock(self):
        """Load clock image"""
        clock_path = os.path.join('char', 'clock.png')
        
        if os.path.exists(clock_path):
            print(f"Loading clock from {clock_path}...")
            self.clock_image = pygame.image.load(clock_path).convert_alpha()
            self.clock_icon = pygame.transform.scale(self.clock_image, 
                                                     (CLOCK_ICON_SIZE, CLOCK_ICON_SIZE))
            # Make clock display same size as white circle (diameter = CLOCK_DISPLAY_SIZE + 20)
            clock_full_size = (CLOCK_DISPLAY_SIZE // 2 + 10) * 2
            self.clock_display = pygame.transform.scale(self.clock_image,
                                                       (clock_full_size, clock_full_size))
        else:
            print("Clock image not found, creating placeholder...")
            # Create simple placeholder clock
            self.clock_icon = pygame.Surface((CLOCK_ICON_SIZE, CLOCK_ICON_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(self.clock_icon, GRAY, 
                             (CLOCK_ICON_SIZE//2, CLOCK_ICON_SIZE//2), 
                             CLOCK_ICON_SIZE//2 - 5)
            pygame.draw.circle(self.clock_icon, WHITE, 
                             (CLOCK_ICON_SIZE//2, CLOCK_ICON_SIZE//2), 
                             CLOCK_ICON_SIZE//2 - 10)
            
            # Make clock display same size as white circle
            clock_full_size = (CLOCK_DISPLAY_SIZE // 2 + 10) * 2
            self.clock_display = pygame.Surface((clock_full_size, clock_full_size), 
                                               pygame.SRCALPHA)
            pygame.draw.circle(self.clock_display, GRAY, 
                             (clock_full_size//2, clock_full_size//2), 
                             clock_full_size//2 - 5)
            pygame.draw.circle(self.clock_display, WHITE, 
                             (clock_full_size//2, clock_full_size//2), 
                             clock_full_size//2 - 10)
    
    def load_map(self):
        """Load map from PNG file or create default"""
        # Try loading from char folder first
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
            # Create a simple default map
            self.map_width = 30 * TILE_SIZE
            self.map_height = 20 * TILE_SIZE
            self.map_image = pygame.Surface((self.map_width, self.map_height))
            
            # Fill with grass pattern
            for y in range(0, self.map_height, TILE_SIZE):
                for x in range(0, self.map_width, TILE_SIZE):
                    # Alternate between two shades of green
                    if ((x // TILE_SIZE) + (y // TILE_SIZE)) % 2 == 0:
                        color = (51, 153, 51)
                    else:
                        color = (41, 143, 41)
                    pygame.draw.rect(self.map_image, color, (x, y, TILE_SIZE, TILE_SIZE))
            
            # Draw a path
            for i in range(20):
                pygame.draw.rect(self.map_image, BROWN, 
                                (3 * TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            
            # Draw a house
            house_color = (139, 115, 85)
            roof_color = (139, 69, 19)
            pygame.draw.rect(self.map_image, house_color, 
                           (10 * TILE_SIZE, 5 * TILE_SIZE, 8 * TILE_SIZE, 6 * TILE_SIZE))
            pygame.draw.rect(self.map_image, roof_color, 
                           (9 * TILE_SIZE, 4 * TILE_SIZE, 10 * TILE_SIZE, TILE_SIZE))
        
        # Scale map for display
        self.map_surface = pygame.transform.scale(
            self.map_image,
            (self.map_width * SCALE, self.map_height * SCALE)
        )
    
    def handle_events(self):
        """Handle game events"""
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
                    # Check if near a tree/bush/trunk and start action
                    if not self.clock_ui_active and not self.watering and not self.picking and not self.cutting:
                        # Try picking first, then cutting, then watering
                        if self.is_near_bush():
                            self.check_picking_action()
                        elif self.is_near_trunk():
                            self.check_cutting_action()
                        else:
                            self.check_watering_action()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
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
        """Handle mouse clicks"""
        # Check if clock icon was clicked
        if self.clock_icon_rect.collidepoint(pos) and not self.clock_ui_active:
            self.clock_ui_active = True
            return
        
        # If clock UI is active, check if hands are being grabbed
        if self.clock_ui_active:
            cx, cy = CLOCK_CENTER_X, CLOCK_CENTER_Y
            dx, dy = pos[0] - cx, pos[1] - cy
            distance = math.sqrt(dx**2 + dy**2)
            
            # Check if clicking near center (to close)
            if distance < 30:
                self.clock_ui_active = False
                return
            
            # Determine which hand is being grabbed
            if distance < CLOCK_DISPLAY_SIZE // 2 - 20:
                # Calculate angle to click point
                angle = math.degrees(math.atan2(dy, dx)) + 90
                if angle < 0:
                    angle += 360
                
                # Check if closer to hour or minute hand
                hour_diff = abs(self.angle_difference(angle, self.hour_angle))
                minute_diff = abs(self.angle_difference(angle, self.minute_angle))
                
                if hour_diff < 20:
                    self.dragging_hand = 'hour'
                elif minute_diff < 20:
                    self.dragging_hand = 'minute'
    
    def angle_difference(self, a1, a2):
        """Calculate shortest difference between two angles"""
        diff = a1 - a2
        while diff > 180:
            diff -= 360
        while diff < -180:
            diff += 360
        return diff
    
    def update_hand_angle(self, pos):
        """Update the angle of the dragged hand"""
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
        """Check if clock is set to specific hour (1-12)"""
        # Convert hour to angle (12 o'clock = 0 degrees, 1 o'clock = 30 degrees, etc.)
        target_angle = (hour % 12) * 30
        # Allow 15 degree tolerance (±15 degrees)
        angle_diff = abs(self.hour_angle - target_angle)
        # Handle wrap-around (e.g., 350 degrees should be close to 0 degrees)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        return angle_diff <= 15
    
    def is_minute_at_12(self):
        """Check if minute hand is pointing at 12 (0 degrees)"""
        # 12 o'clock position = 0 degrees (or 360 degrees)
        # Allow 15 degree tolerance (±15 degrees)
        angle_diff = min(abs(self.minute_angle - 0), abs(self.minute_angle - 360))
        return angle_diff <= 15
    
    def is_near_tree(self):
        """Check if player is near any tree"""
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
        """Check if player is near any unpicked bush"""
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
        """Check if player is near any uncut trunk"""
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
    
    def check_trunk_collision(self, new_x, new_y):
        """Check if new position collides with any uncut trunk"""
        # Player hitbox (smaller than sprite for better feel)
        player_size = 12
        player_left = new_x
        player_right = new_x + player_size
        player_top = new_y
        player_bottom = new_y + player_size
        
        for trunk in self.trunks:
            if not trunk['cut']:
                # Trunk hitbox (64x64 sprite, using slightly smaller collision box)
                trunk_size = 50
                trunk_left = trunk['x']
                trunk_right = trunk['x'] + trunk_size
                trunk_top = trunk['y']
                trunk_bottom = trunk['y'] + 25
                
                # Check for overlap
                if (player_right > trunk_left and player_left < trunk_right and
                    player_bottom > trunk_top and player_top < trunk_bottom):
                    return True
        return False
    
    def check_watering_action(self):
        """Check if player is near a tree and start watering"""
        # Check if clock is set to correct time for active mission
        mission = self.missions[0]  # First mission
        if not mission['completed'] and not self.is_clock_set_to_hour(mission['required_hour']):
            # Clock not set to correct time, show message
            print(f"Set jam ke {mission['required_hour']:02d}:00 terlebih dahulu!")
            return
        
        player_x = self.player['x']
        player_y = self.player['y']
        
        for tree in self.trees:
            # Check distance to tree (within 70 pixels)
            dx = tree['x'] - player_x
            dy = tree['y'] - player_y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < 70:
                # Determine if tree is on left or right
                if dx < 0:
                    self.watering_side = 'left'
                else:
                    self.watering_side = 'right'
                
                self.watering = True
                self.watering_timer = 0
                
                # Complete mission if not completed
                if not mission['completed']:
                    mission['completed'] = True
                    self.notification_text = f"MISI SELESAI: {mission['title']}!"
                    self.notification_timer = 0
                    print(f"Misi selesai: {mission['title']}!")
                
                return
    
    def check_picking_action(self):
        """Check if player is near a bush and start picking"""
        # Check if clock is set to correct time for picking mission
        mission = self.missions[1]  # Second mission (picking)
        if not mission['completed']:
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
                    # Pick the fruit
                    bush['picked'] = True
                    self.picking = True
                    self.picking_timer = 0
                    self.fruits_picked += 1
                    
                    # Check if mission is completed
                    if self.fruits_picked >= 3:
                        mission = self.missions[1]  # Second mission
                        if not mission['completed']:
                            mission['completed'] = True
                            self.notification_text = f"MISI SELESAI: {mission['title']}!"
                            self.notification_timer = 0
                            print(f"Misi selesai: {mission['title']}!")
                    
                    return
    
    def check_cutting_action(self):
        """Check if player is near a trunk and start cutting"""
        # Check if clock is set to correct time for cutting mission
        mission = self.missions[2]  # Third mission (cutting)
        if not mission['completed']:
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
                    # Determine trunk position relative to player
                    if abs(dx) > abs(dy):
                        # Trunk is more to the side
                        if dx < 0:
                            self.cutting_side = 'left'
                        else:
                            self.cutting_side = 'right'
                    else:
                        # Trunk is more above/below
                        if dy < 0:
                            self.cutting_side = 'behind'
                        else:
                            self.cutting_side = 'front'
                    
                    # Cut the trunk
                    trunk['cut'] = True
                    self.cutting = True
                    self.cutting_timer = 0
                    self.trunks_cut += 1
                    
                    # Check if mission is completed
                    if self.trunks_cut >= 2:
                        mission = self.missions[2]  # Third mission
                        if not mission['completed']:
                            mission['completed'] = True
                            self.notification_text = f"MISI SELESAI: {mission['title']}!"
                            self.notification_timer = 0
                            print(f"Misi selesai: {mission['title']}!")
                    
                    return
    
    def update(self, dt):
        """Update game state"""
        # Update notification timer
        if self.notification_timer < self.notification_duration:
            self.notification_timer += dt
        
        # Update picking animation (but allow movement)
        if self.picking:
            self.picking_timer += dt
            if self.picking_timer >= self.picking_duration:
                self.picking = False
                self.picking_timer = 0
            # Don't return - allow player to move while showing fruit
        
        # Update cutting animation
        if self.cutting:
            self.cutting_timer += dt
            if self.cutting_timer >= self.cutting_duration:
                self.cutting = False
                self.cutting_timer = 0
            # Update animation during cutting
            self.player['animation_timer'] += dt
            if self.player['animation_timer'] >= self.animation_speed:
                self.player['animation_timer'] = 0
                self.player['animation_frame'] = (self.player['animation_frame'] + 1) % 2
            return
        
        # Update watering animation
        if self.watering:
            self.watering_timer += dt
            if self.watering_timer >= self.watering_duration:
                self.watering = False
                self.watering_timer = 0
            # Update animation during watering
            self.player['animation_timer'] += dt
            if self.player['animation_timer'] >= self.animation_speed:
                self.player['animation_timer'] = 0
                self.player['animation_frame'] = (self.player['animation_frame'] + 1) % 2
            return
        
        # Only update player if clock UI is not active
        if not self.clock_ui_active:
            keys = pygame.key.get_pressed()
            moving = False
            dx, dy = 0, 0
            
            # Handle movement
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
            
            # Update player position
            if moving:
                # Calculate new position
                new_x = self.player['x'] + dx
                new_y = self.player['y'] + dy
                
                # Check collision with trunks
                if not self.check_trunk_collision(new_x, new_y):
                    self.player['x'] = new_x
                    self.player['y'] = new_y
                    self.player['state'] = 'walking'
                else:
                    # Try moving only horizontally
                    if dx != 0 and not self.check_trunk_collision(self.player['x'] + dx, self.player['y']):
                        self.player['x'] += dx
                        self.player['state'] = 'walking'
                    # Try moving only vertically
                    elif dy != 0 and not self.check_trunk_collision(self.player['x'], self.player['y'] + dy):
                        self.player['y'] += dy
                        self.player['state'] = 'walking'
                    else:
                        self.player['state'] = 'idle'
            else:
                self.player['state'] = 'idle'
            
            # Keep player within bounds
            self.player['x'] = max(0, min(self.player['x'], 
                                         self.map_width - self.player['width']))
            self.player['y'] = max(0, min(self.player['y'], 
                                         self.map_height - self.player['height']))
            
            # Update animation
            self.player['animation_timer'] += dt
            if self.player['animation_timer'] >= self.animation_speed:
                self.player['animation_timer'] = 0
                self.player['animation_frame'] = (self.player['animation_frame'] + 1) % 2
            
            # Update camera
            self.camera_x = self.player['x'] - (SCREEN_WIDTH // (2 * SCALE)) + self.player['width'] // 2
            self.camera_y = self.player['y'] - (SCREEN_HEIGHT // (2 * SCALE)) + self.player['height'] // 2
            
            # Keep camera within bounds
            self.camera_x = max(0, min(self.camera_x, self.map_width - SCREEN_WIDTH // SCALE))
            self.camera_y = max(0, min(self.camera_y, self.map_height - SCREEN_HEIGHT // SCALE))
    
    def draw(self):
        """Draw game"""
        self.screen.fill(BLACK)
        
        # Draw map
        map_x = -self.camera_x * SCALE
        map_y = -self.camera_y * SCALE
        self.screen.blit(self.map_surface, (map_x, map_y))
        
        # Prepare player sprite data
        state = self.player['state']
        frame = self.player['animation_frame'] + 1
        
        # Map state to sprite key
        if state == 'idle':
            sprite_key = f'idle{frame}'
        else:  # walking
            sprite_key = f'walk{frame}'
        
        player_screen_x = (self.player['x'] - self.camera_x) * SCALE
        player_screen_y = (self.player['y'] - self.camera_y) * SCALE
        
        # Update sprite key for animations
        if self.watering:
            frame = self.player['animation_frame'] + 1
            sprite_key = f'watering-{self.watering_side}{frame}'
        elif self.cutting:
            frame = self.player['animation_frame'] + 1
            sprite_key = f'cut-{self.cutting_side}{frame}'
        
        # Create list of all entities to draw with their depth (Y position)
        entities = []
        
        # Add player (use bottom of sprite in map coordinates)
        entities.append({
            'type': 'player',
            'y': self.player['y'] + 16,  # Bottom of player sprite (16x16 in map coords, 32x32 on screen)
            'sprite': self.sprites[sprite_key],
            'x': player_screen_x,
            'screen_y': player_screen_y
        })
        
        # Add trees (128x128 screen pixels = 64x64 map pixels)
        for tree in self.trees:
            entities.append({
                'type': 'tree',
                'y': tree['y'] + 64,  # Bottom of tree sprite in map coordinates
                'sprite': self.tree_sprite,
                'x': (tree['x'] - self.camera_x) * SCALE,
                'screen_y': (tree['y'] - self.camera_y) * SCALE
            })
        
        # Add trunks (64x64 screen pixels = 32x32 map pixels)
        for trunk in self.trunks:
            if not trunk['cut']:
                entities.append({
                    'type': 'trunk',
                    'y': trunk['y'] + 32,  # Bottom of trunk sprite in map coordinates
                    'sprite': self.trunk_sprite,
                    'x': (trunk['x'] - self.camera_x) * SCALE,
                    'screen_y': (trunk['y'] - self.camera_y) * SCALE
                })
        
        # Add bushes (64x64 screen pixels = 32x32 map pixels)
        for bush in self.bushes:
            bush_sprite = self.bush2_sprite if bush['picked'] else self.bush1_sprite
            entities.append({
                'type': 'bush',
                'y': bush['y'] + 32,  # Bottom of bush sprite in map coordinates
                'sprite': bush_sprite,
                'x': (bush['x'] - self.camera_x) * SCALE,
                'screen_y': (bush['y'] - self.camera_y) * SCALE
            })
        
        # Sort entities by Y position (depth)
        entities.sort(key=lambda e: e['y'])
        
        # Draw all entities in sorted order
        for entity in entities:
            self.screen.blit(entity['sprite'], (entity['x'], entity['screen_y']))
        
        # Draw fruit above player if picking (always on top)
        if self.picking:
            fruit_x = player_screen_x + 8
            fruit_y = player_screen_y - 40
            self.screen.blit(self.fruit_sprite, (fruit_x, fruit_y))
        
        # Draw clock icon
        self.screen.blit(self.clock_icon, (10, 10))
        
        # Draw mission box
        self.draw_mission_box()
        
        # Draw clock UI if active
        if self.clock_ui_active:
            self.draw_clock_ui()
        
        # Draw watering prompt
        self.draw_watering_prompt()
        
        # Draw notification
        self.draw_notification()
        
        # Draw debug info
        self.draw_debug_info()
        
        pygame.display.flip()
    
    def draw_mission_box(self):
        """Draw mission box next to clock icon"""
        # Background box (bigger for 3 missions)
        mission_bg = pygame.Surface((300, 180))
        mission_bg.set_alpha(200)
        mission_bg.fill((40, 40, 60))
        self.screen.blit(mission_bg, (150, 10))
        
        # Border
        pygame.draw.rect(self.screen, WHITE, (150, 10, 300, 180), 2)
        
        # Title
        font_title = pygame.font.Font(None, 28)
        title_surface = font_title.render("MISI", True, (255, 215, 0))
        self.screen.blit(title_surface, (160, 20))
        
        # Mission list
        font_mission = pygame.font.Font(None, 22)
        y_offset = 50
        
        for mission in self.missions:
            # Mission status icon
            status_color = (0, 255, 0) if mission['completed'] else (255, 100, 100)
            status_text = "✓" if mission['completed'] else "○"
            status_surface = font_mission.render(status_text, True, status_color)
            self.screen.blit(status_surface, (160, y_offset))
            
            # Mission title
            title_color = (0, 255, 0) if mission['completed'] else WHITE
            mission_surface = font_mission.render(mission['title'], True, title_color)
            self.screen.blit(mission_surface, (185, y_offset))
            
            # Mission description (smaller)
            if not mission['completed']:
                font_desc = pygame.font.Font(None, 18)
                desc_surface = font_desc.render(mission['description'], True, (180, 180, 180))
                self.screen.blit(desc_surface, (185, y_offset + 22))
            
            y_offset += 60
    
    def draw_notification(self):
        """Draw notification message"""
        if self.notification_timer < self.notification_duration and self.notification_text:
            font = pygame.font.Font(None, 36)
            text_surface = font.render(self.notification_text, True, (0, 255, 0))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
            
            # Background
            bg_rect = text_rect.inflate(40, 20)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.set_alpha(200)
            bg_surface.fill((20, 20, 40))
            self.screen.blit(bg_surface, bg_rect.topleft)
            
            # Border
            pygame.draw.rect(self.screen, (0, 255, 0), bg_rect, 3)
            
            # Text
            self.screen.blit(text_surface, text_rect)
    
    def draw_watering_prompt(self):
        """Draw action prompt at bottom of screen"""
        if not self.watering and not self.picking and not self.cutting and not self.clock_ui_active:
            text = None
            
            if self.is_near_bush():
                text = "Tekan E untuk memetik buah"
            elif self.is_near_trunk():
                text = "Tekan E untuk singkirkan kayu"
            elif self.is_near_tree():
                text = "Tekan E untuk menyiram pohon"
            
            if text:
                font = pygame.font.Font(None, 28)
                text_surface = font.render(text, True, WHITE)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
                
                # Background
                bg_rect = text_rect.inflate(30, 15)
                bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
                bg_surface.set_alpha(180)
                bg_surface.fill((40, 40, 60))
                self.screen.blit(bg_surface, bg_rect.topleft)
                
                # Border
                pygame.draw.rect(self.screen, (100, 150, 255), bg_rect, 2)
                
                # Text
                self.screen.blit(text_surface, text_rect)
    
    def draw_clock_ui(self):
        """Draw interactive clock interface"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw clock image
        cx, cy = CLOCK_CENTER_X, CLOCK_CENTER_Y
        clock_radius = CLOCK_DISPLAY_SIZE // 2 + 10
        
        # Draw clock image (same size as white circle)
        clock_full_size = clock_radius * 2
        clock_x = cx - clock_radius
        clock_y = cy - clock_radius
        self.screen.blit(self.clock_display, (clock_x, clock_y))
        
        # Draw hour markers
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            outer_radius = CLOCK_DISPLAY_SIZE // 2 - 20
            inner_radius = outer_radius - 15
            
            x1 = cx + math.cos(angle) * inner_radius
            y1 = cy + math.sin(angle) * inner_radius
            x2 = cx + math.cos(angle) * outer_radius
            y2 = cy + math.sin(angle) * outer_radius
            
            pygame.draw.line(self.screen, BLACK, (x1, y1), (x2, y2), 3)
        
        # Draw minute hand (longer, thinner)
        minute_angle_rad = math.radians(self.minute_angle - 90)
        minute_length = CLOCK_DISPLAY_SIZE // 2 - 250
        minute_x = cx + math.cos(minute_angle_rad) * minute_length
        minute_y = cy + math.sin(minute_angle_rad) * minute_length
        pygame.draw.line(self.screen, DARK_BLUE, (cx, cy), (minute_x, minute_y), 4)
        
        # Draw hour hand (shorter, thicker)
        hour_angle_rad = math.radians(self.hour_angle - 90)
        hour_length = CLOCK_DISPLAY_SIZE // 2 - 320
        hour_x = cx + math.cos(hour_angle_rad) * hour_length
        hour_y = cy + math.sin(hour_angle_rad) * hour_length
        pygame.draw.line(self.screen, RED, (cx, cy), (hour_x, hour_y), 6)
        
        # Draw center circle
        pygame.draw.circle(self.screen, BLACK, (cx, cy), 12)
        pygame.draw.circle(self.screen, WHITE, (cx, cy), 8)
        
        # Draw instructions
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
    
    def draw_debug_info(self):
        """Draw debug information"""
        font = pygame.font.Font(None, 24)
        
        # Background
        info_bg = pygame.Surface((200, 80))
        info_bg.set_alpha(180)
        info_bg.fill(BLACK)
        self.screen.blit(info_bg, (5, 5))
        
        # Text
        texts = [
            f"Pos: {int(self.player['x'])}, {int(self.player['y'])}",
            f"State: {self.player['state']}",
            f"Direction: {self.player['direction']}",
            f"FPS: {int(self.clock.get_fps())}"
        ]
        
        y = 10
        for text in texts:
            surface = font.render(text, True, WHITE)
            self.screen.blit(surface, (10, y))
            y += 20
    
    def run(self):
        """Main game loop"""
        print("\n=== Game Started ===")
        print("Controls:")
        print("  Arrow Keys atau WASD - Move")
        print("  SPASI atau E - Water tree (when near)")
        print("  Click Clock Icon - Buka UI jam")
        print("  Drag Clock Hands - Set Waktu")
        print("  ESC - Close Clock / Quit")
        print("========================\n")
        
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()
