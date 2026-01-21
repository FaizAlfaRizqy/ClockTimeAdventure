"""
Classic 2D RPG Game - Python Pygame Version
Map menggunakan file PNG, sprite menggunakan idle1.png, idle2.png, walk1.png, walk2.png
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
        pygame.display.set_caption("Classic RPG - Backyard Adventure")
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
    
    def update(self, dt):
        """Update game state"""
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
                self.player['x'] += dx
                self.player['y'] += dy
                self.player['state'] = 'walking'
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
        
        # Draw player
        state = self.player['state']
        frame = self.player['animation_frame'] + 1
        
        # Map state to sprite key
        if state == 'idle':
            sprite_key = f'idle{frame}'
        else:  # walking
            sprite_key = f'walk{frame}'
        
        player_screen_x = (self.player['x'] - self.camera_x) * SCALE
        player_screen_y = (self.player['y'] - self.camera_y) * SCALE
        self.screen.blit(self.sprites[sprite_key], (player_screen_x, player_screen_y))
        
        # Draw clock icon
        self.screen.blit(self.clock_icon, (10, 10))
        
        # Draw clock UI if active
        if self.clock_ui_active:
            self.draw_clock_ui()
        
        # Draw debug info
        self.draw_debug_info()
        
        pygame.display.flip()
    
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
        print("\n=== Classic RPG Started ===")
        print("Controls:")
        print("  Arrow Keys or WASD - Move")
        print("  Click Clock Icon - Open Clock UI")
        print("  Drag Clock Hands - Set Time")
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
