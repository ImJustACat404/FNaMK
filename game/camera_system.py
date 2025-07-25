import pygame
import random
from typing import Dict, Tuple
from .constants import *
from .enums import CameraView, Location

class CameraSystem:
    def __init__(self):
        self.current_view = CameraView.OFFICE
        self.camera_static = False
        self.static_timer = 0
        
        # Small camera map positions (moved higher to avoid button overlap)
        self.small_map_positions = {
            # Starting areas (far from office)
            CameraView.STAGE: (850, 450, 60, 40),
            CameraView.BACKSTAGE: (920, 450, 60, 40),
            CameraView.SUPPLY_CLOSET: (990, 450, 60, 40),
            
            # Intermediate areas
            CameraView.DINING_AREA: (850, 500, 60, 40),
            CameraView.KITCHEN: (920, 500, 60, 40),
            CameraView.BATHROOM: (990, 500, 60, 40),
            CameraView.STORAGE_ROOM: (1060, 500, 60, 40),
            
            # Approach areas (closer to office)
            CameraView.HALLWAY_LEFT: (850, 550, 60, 40),
            CameraView.HALLWAY_RIGHT: (920, 550, 60, 40),
            CameraView.VENT_LEFT: (990, 550, 60, 40),
            CameraView.VENT_RIGHT: (1060, 550, 60, 40),
            
            # Office (center)
            CameraView.OFFICE: (1060, 450, 60, 40),
        }
        
        # Camera labels for the small map
        self.camera_labels = {
            CameraView.STAGE: "1A",
            CameraView.BACKSTAGE: "1B", 
            CameraView.SUPPLY_CLOSET: "1C",
            CameraView.DINING_AREA: "2A",
            CameraView.KITCHEN: "2B",
            CameraView.BATHROOM: "2C",
            CameraView.STORAGE_ROOM: "3A",
            CameraView.HALLWAY_LEFT: "4A",
            CameraView.HALLWAY_RIGHT: "4B",
            CameraView.VENT_LEFT: "5A",
            CameraView.VENT_RIGHT: "5B",
            CameraView.OFFICE: "OFF"
        }
    
    def switch_to_office(self):
        """Switch back to office view."""
        self.current_view = CameraView.OFFICE
        self.camera_static = True
        self.static_timer = 0.5
    
    def switch_to_camera(self, camera_view: CameraView):
        """Switch to a specific camera view."""
        self.current_view = camera_view
        self.camera_static = True
        self.static_timer = 0.5
    
    def cycle_camera_views(self):
        """Cycle through available camera views."""
        views = list(CameraView)
        current_index = views.index(self.current_view)
        next_index = (current_index + 1) % len(views)
        self.current_view = views[next_index]
        self.camera_static = True
        self.static_timer = 0.3
    
    def update_static(self, dt: float):
        """Update camera static effect."""
        if self.camera_static:
            self.static_timer -= dt
            if self.static_timer <= 0:
                self.camera_static = False
    
    def draw_camera_view(self, screen, animatronics):
        """Draw the classic FNAF camera view with small map."""
        # Fill screen with black
        screen.fill(BLACK)
        
        # Camera static effect
        if self.camera_static:
            for _ in range(100):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                pygame.draw.circle(screen, WHITE, (x, y), 1)
        
        # Main camera view area (most of screen)
        camera_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200)
        pygame.draw.rect(screen, DARK_GRAY, camera_rect)
        
        # Scan lines effect
        for y in range(50, SCREEN_HEIGHT - 150, 4):
            pygame.draw.line(screen, (0, 0, 0, 50), (50, y), (SCREEN_WIDTH - 200, y), 1)
        
        # Show animatronics in current camera view
        for animatronic in animatronics:
            if animatronic.current_location.value == self.current_view.value:
                self.draw_animatronic_in_camera(screen, animatronic, camera_rect)
        
        # Camera label (top right)
        font = pygame.font.Font(None, 36)
        label = font.render(f"Camera: {self.current_view.value}", True, WHITE)
        screen.blit(label, (SCREEN_WIDTH - 250, 20))
        
        # Time display (top right)
        time_font = pygame.font.Font(None, 24)
        time_text = time_font.render("LIVE", True, RED)
        screen.blit(time_text, (SCREEN_WIDTH - 100, 20))
        
        # Draw small camera map (moved higher)
        self.draw_small_camera_map(screen)
    
    def draw_small_camera_map(self, screen):
        """Draw the small camera map (no animatronic locations shown)."""
        # Map background
        map_rect = pygame.Rect(840, 440, 290, 160)
        pygame.draw.rect(screen, DARK_GRAY, map_rect)
        pygame.draw.rect(screen, WHITE, map_rect, 2)
        
        # Draw camera areas
        for camera_view, (x, y, w, h) in self.small_map_positions.items():
            # Determine color based on distance from office
            if camera_view == CameraView.OFFICE:
                color = GREEN  # Office
            elif camera_view in [CameraView.VENT_LEFT, CameraView.VENT_RIGHT, CameraView.HALLWAY_LEFT, CameraView.HALLWAY_RIGHT]:
                color = RED  # Dangerous areas
            elif camera_view in [CameraView.DINING_AREA, CameraView.KITCHEN, CameraView.BATHROOM, CameraView.STORAGE_ROOM]:
                color = YELLOW  # Intermediate areas
            else:
                color = BLUE  # Starting areas
            
            # Camera area background
            pygame.draw.rect(screen, BLACK, (x, y, w, h))
            pygame.draw.rect(screen, color, (x, y, w, h), 2)
            
            # Camera label
            small_font = pygame.font.Font(None, 16)
            label = self.camera_labels.get(camera_view, "??")
            label_text = small_font.render(label, True, WHITE)
            label_rect = label_text.get_rect(center=(x + w // 2, y + h // 2))
            screen.blit(label_text, label_rect)
            
            # Highlight current view
            if camera_view == self.current_view:
                pygame.draw.rect(screen, WHITE, (x, y, w, h), 3)
        
        # Map title
        title_font = pygame.font.Font(None, 20)
        title = title_font.render("CAMERA MAP", True, WHITE)
        screen.blit(title, (850, 420))
    
    def draw_animatronic_in_camera(self, screen, animatronic, camera_rect):
        """Draw animatronic in the main camera view."""
        colors = {
            "Freddy": BROWN,
            "Bonnie": BLUE,
            "Chica": YELLOW,
            "Foxy": ORANGE,
            "Golden Freddy": GOLD
        }
        
        color = colors.get(animatronic.name.value, WHITE)
        
        # Position animatronic in camera view
        animatronic_x = camera_rect.x + camera_rect.width // 2
        animatronic_y = camera_rect.y + camera_rect.height // 2
        
        # Draw animatronic body
        animatronic_rect = pygame.Rect(animatronic_x - 50, animatronic_y - 75, 100, 150)
        pygame.draw.rect(screen, color, animatronic_rect)
        
        # Add details based on animatronic type
        if animatronic.name.value == "Freddy":
            # Hat
            hat_rect = pygame.Rect(animatronic_x - 60, animatronic_y - 95, 120, 20)
            pygame.draw.rect(screen, BROWN, hat_rect)
            # Bow tie
            bow_rect = pygame.Rect(animatronic_x - 15, animatronic_y - 35, 30, 15)
            pygame.draw.rect(screen, RED, bow_rect)
        
        # Eyes (glowing effect)
        eye_color = (255, 0, 0)  # Red eyes in camera view
        pygame.draw.circle(screen, eye_color, (animatronic_x - 25, animatronic_y - 45), 8)
        pygame.draw.circle(screen, eye_color, (animatronic_x + 25, animatronic_y - 45), 8)
        
        # Name label
        font = pygame.font.Font(None, 24)
        name_text = font.render(animatronic.name.value, True, WHITE)
        screen.blit(name_text, (animatronic_x - 40, animatronic_y - 95))
        
        # Watching indicator
        if animatronic.is_being_watched:
            pygame.draw.rect(screen, GREEN, animatronic_rect, 3)
            watch_text = font.render("WATCHED", True, GREEN)
            screen.blit(watch_text, (animatronic_x - 40, animatronic_y - 115))
    
    def handle_small_map_click(self, pos):
        """Handle clicks on the small camera map."""
        for camera_view, (x, y, w, h) in self.small_map_positions.items():
            if x <= pos[0] <= x + w and y <= pos[1] <= y + h:
                if camera_view == CameraView.OFFICE:
                    return "office"
                else:
                    return camera_view
        return None
    
    def get_small_map_rects(self):
        """Get small map rectangles for click detection."""
        return self.small_map_positions 