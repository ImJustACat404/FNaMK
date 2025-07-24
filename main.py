import pygame
import random
import time
import json
from typing import List

from game.constants import *
from game.enums import *
from game.animatronic import Animatronic
from game.camera_system import CameraSystem
from game.animatronic_ai import AnimatronicAI
from game.ui_system import UISystem

class FNAFGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Five Nights at Freddy's Enhanced")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.game_state = GameState.MENU
        self.current_night = 1
        self.current_hour = 12  # 12 AM
        self.current_minute = 0
        self.last_time_update = time.time()
        
        # Power management
        self.current_power = MAX_POWER
        
        # Office controls
        self.left_door_closed = False
        self.right_door_closed = False
        self.left_light_on = False
        self.right_light_on = False
        self.vent_system_active = False
        self.emergency_power = False
        self.emergency_power_remaining = 30
        
        # Game systems
        self.camera_system = CameraSystem()
        self.animatronic_ai = AnimatronicAI()
        self.ui_system = UISystem()
        
        # Animatronics
        self.animatronics = self.initialize_animatronics()
        
        # Game mechanics
        self.jumpscare_active = False
        self.jumpscare_timer = 0
        self.flash_effect = False
        self.flash_timer = 0
        self.screen_shake = False
        self.shake_timer = 0
        
        # Statistics
        self.nights_survived = 0
        self.total_jumpscares = 0
        self.best_survival_time = 0
        self.total_score = 0
        self.survival_bonus = 0
        
        # Load saved statistics
        self.load_statistics()
    
    def initialize_animatronics(self) -> List[Animatronic]:
        """Initialize all animatronics with their starting positions and behaviors."""
        return [
            Animatronic(
                name=AnimatronicType.FREDDY,
                current_location=Location.STAGE,  # Starts far from office
                target_location=Location.STAGE,
                movement_speed=0.3,
                aggression=0.4,
                jumscare_chance=0.1
            ),
            Animatronic(
                name=AnimatronicType.BONNIE,
                current_location=Location.STAGE,  # Starts far from office
                target_location=Location.STAGE,
                movement_speed=0.5,
                aggression=0.6,
                jumscare_chance=0.15
            ),
            Animatronic(
                name=AnimatronicType.CHICA,
                current_location=Location.STAGE,  # Starts far from office
                target_location=Location.STAGE,
                movement_speed=0.4,
                aggression=0.5,
                jumscare_chance=0.12
            ),
            Animatronic(
                name=AnimatronicType.FOXY,
                current_location=Location.BACKSTAGE,  # Starts in backstage, far from office
                target_location=Location.BACKSTAGE,
                movement_speed=0.8,
                aggression=0.7,
                jumscare_chance=0.2
            ),
            Animatronic(
                name=AnimatronicType.GOLDEN_FREDDY,
                current_location=Location.SUPPLY_CLOSET,  # Starts in supply closet, far from office
                target_location=Location.SUPPLY_CLOSET,
                movement_speed=0.2,
                aggression=0.9,
                jumscare_chance=0.3,
                is_active=False  # Only active on later nights
            )
        ]
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == GameState.PLAYING:
                        if self.camera_system.current_view != CameraView.OFFICE:
                            self.camera_system.switch_to_office()
                        else:
                            self.game_state = GameState.PAUSED
                    elif self.game_state == GameState.PAUSED:
                        self.game_state = GameState.PLAYING
                
                # Enhanced quick controls
                if self.game_state == GameState.PLAYING:
                    if event.key == pygame.K_1:
                        self.toggle_left_door()
                    elif event.key == pygame.K_2:
                        self.toggle_right_door()
                    elif event.key == pygame.K_3:
                        self.toggle_left_light()
                    elif event.key == pygame.K_4:
                        self.toggle_right_light()
                    elif event.key == pygame.K_c:
                        self.game_state = GameState.CAMERA_MAP
                    elif event.key == pygame.K_v:
                        self.toggle_vent_system()
                    elif event.key == pygame.K_e:
                        self.activate_emergency_power()
                    elif event.key == pygame.K_TAB:
                        self.camera_system.cycle_camera_views()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_state == GameState.MENU:
                    self.handle_menu_click(event.pos)
                elif self.game_state == GameState.PLAYING:
                    self.handle_game_click(event.pos)
                elif self.game_state == GameState.GAME_OVER:
                    self.handle_game_over_click(event.pos)
                elif self.game_state == GameState.VICTORY:
                    self.handle_victory_click(event.pos)
        
        return True
    
    def handle_menu_click(self, pos):
        """Handle clicks on the enhanced main menu."""
        # Start game button
        start_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 250, 200, 50)
        if start_rect.collidepoint(pos):
            self.start_new_game()
        
        # Custom night button
        custom_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 310, 200, 50)
        if custom_rect.collidepoint(pos):
            self.current_night = 3
            self.start_new_game()
        
        # Statistics button
        stats_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 370, 200, 50)
        if stats_rect.collidepoint(pos):
            self.draw_statistics()
        
        # Quit button
        quit_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 430, 200, 50)
        if quit_rect.collidepoint(pos):
            return False
    
    def handle_game_click(self, pos):
        """Handle clicks during gameplay."""
        button_name = self.ui_system.handle_button_click(pos)
        if button_name:
            if button_name == 'left_door':
                self.toggle_left_door()
            elif button_name == 'right_door':
                self.toggle_right_door()
            elif button_name == 'left_light':
                self.toggle_left_light()
            elif button_name == 'right_light':
                self.toggle_right_light()
            elif button_name == 'camera':
                # Switch to camera view instead of camera map
                if self.camera_system.current_view == CameraView.OFFICE:
                    self.camera_system.switch_to_camera(CameraView.STAGE)
                else:
                    self.camera_system.switch_to_office()
            elif button_name == 'vent':
                self.toggle_vent_system()
            elif button_name == 'emergency_power':
                self.activate_emergency_power()
        
        # Handle clicks on small camera map when in camera view
        if self.camera_system.current_view != CameraView.OFFICE:
            result = self.camera_system.handle_small_map_click(pos)
            if result == "office":
                self.camera_system.switch_to_office()
            elif result:
                self.camera_system.switch_to_camera(result)
    
    # Removed handle_camera_map_click method as it's now handled in handle_game_click
    
    def handle_game_over_click(self, pos):
        """Handle clicks on game over screen."""
        restart_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 450, 200, 50)
        if restart_rect.collidepoint(pos):
            self.game_state = GameState.MENU
    
    def handle_victory_click(self, pos):
        """Handle clicks on victory screen."""
        if self.current_night < 5:
            # Continue to next night button
            next_night_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 450, 300, 50)
            if next_night_rect.collidepoint(pos):
                self.start_next_night()
                return
            
            # Return to menu button
            menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 520, 200, 50)
            if menu_rect.collidepoint(pos):
                self.game_state = GameState.MENU
                return
        else:
            # Final victory - return to menu
            restart_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 450, 200, 50)
            if restart_rect.collidepoint(pos):
                self.game_state = GameState.MENU
    
    def toggle_left_door(self):
        """Toggle left door with enhanced feedback."""
        self.left_door_closed = not self.left_door_closed
        if self.left_door_closed:
            self.flash_effect = True
            self.flash_timer = 0.1
    
    def toggle_right_door(self):
        """Toggle right door with enhanced feedback."""
        self.right_door_closed = not self.right_door_closed
        if self.right_door_closed:
            self.flash_effect = True
            self.flash_timer = 0.1
    
    def toggle_left_light(self):
        """Toggle left light with enhanced feedback."""
        self.left_light_on = not self.left_light_on
    
    def toggle_right_light(self):
        """Toggle right light with enhanced feedback."""
        self.right_light_on = not self.right_light_on
    
    def toggle_vent_system(self):
        """Toggle vent system with enhanced feedback."""
        self.vent_system_active = not self.vent_system_active
        if self.vent_system_active:
            self.flash_effect = True
            self.flash_timer = 0.2
    
    def activate_emergency_power(self):
        """Activate emergency power system with enhanced effects."""
        if not self.emergency_power and self.emergency_power_remaining > 0:
            self.emergency_power = True
            self.current_power = min(self.current_power + 20, MAX_POWER)
            self.flash_effect = True
            self.flash_timer = 0.5
            self.screen_shake = True
            self.shake_timer = 0.3
    
    def start_new_game(self):
        """Start a new game."""
        self.game_state = GameState.PLAYING
        self.current_hour = 12
        self.current_minute = 0
        self.current_power = MAX_POWER
        self.reset_animatronics()
        self.jumpscare_active = False
        self.vent_system_active = False
        self.emergency_power = False
        self.emergency_power_remaining = 30
        self.camera_system.switch_to_office()
    
    def start_next_night(self):
        """Start the next night with increased difficulty."""
        self.current_night += 1
        self.current_hour = 12
        self.current_minute = 0
        self.current_power = MAX_POWER
        self.reset_animatronics()
        self.jumpscare_active = False
        self.vent_system_active = False
        self.emergency_power = False
        self.emergency_power_remaining = 30
        self.camera_system.switch_to_office()
    
    def reset_animatronics(self):
        """Reset animatronics to their starting positions."""
        for animatronic in self.animatronics:
            if animatronic.name == AnimatronicType.FREDDY:
                animatronic.current_location = Location.STAGE  # Starting area - far from office
            elif animatronic.name == AnimatronicType.BONNIE:
                animatronic.current_location = Location.STAGE  # Starting area - far from office
            elif animatronic.name == AnimatronicType.CHICA:
                animatronic.current_location = Location.STAGE  # Starting area - far from office
            elif animatronic.name == AnimatronicType.FOXY:
                animatronic.current_location = Location.BACKSTAGE  # Starting area - far from office
            elif animatronic.name == AnimatronicType.GOLDEN_FREDDY:
                animatronic.current_location = Location.SUPPLY_CLOSET  # Starting area - far from office
                animatronic.is_active = self.current_night >= 3
            
            animatronic.target_location = animatronic.current_location
            animatronic.last_move_time = time.time()
            animatronic.is_being_watched = False
            animatronic.watching_timer = 0
            animatronic.last_seen_location = animatronic.current_location
    
    def update_time(self):
        """Update the in-game time."""
        current_time = time.time()
        time_diff = current_time - self.last_time_update
        
        if time_diff >= TIME_PER_HOUR / 60:  # Update every minute
            self.current_minute += 1
            self.last_time_update = current_time
            
            if self.current_minute >= 60:
                self.current_minute = 0
                self.current_hour += 1
                
                if self.current_hour >= 6:  # 6 AM - Victory!
                    self.game_state = GameState.VICTORY
                    self.calculate_survival_bonus()
    
    def update_power(self):
        """Update power consumption with enhanced mechanics."""
        if self.emergency_power:
            self.emergency_power_remaining -= 1 / FPS
            if self.emergency_power_remaining <= 0:
                self.emergency_power = False
                self.emergency_power_remaining = 0
        else:
            # Normal power drain
            power_drain = POWER_DRAIN_RATE / FPS
            
            # Door power consumption
            if self.left_door_closed:
                power_drain += DOOR_POWER_COST / FPS
            if self.right_door_closed:
                power_drain += DOOR_POWER_COST / FPS
            
            # Light power consumption
            if self.left_light_on:
                power_drain += LIGHT_POWER_COST / FPS
            if self.right_light_on:
                power_drain += LIGHT_POWER_COST / FPS
            
            # Vent system power consumption
            if self.vent_system_active:
                power_drain += VENT_POWER_COST / FPS
            
            self.current_power -= power_drain
            
            # Power warning effects
            if self.current_power <= 40 and not self.emergency_power:  # Increased warning threshold
                if random.random() < 0.05:  # Reduced frequency
                    self.flash_effect = True
                    self.flash_timer = 0.1
            
            if self.current_power <= 0:
                self.current_power = 0
                self.game_state = GameState.GAME_OVER
    
    def update_animatronics(self):
        """Update animatronic positions and behaviors."""
        current_time = time.time()
        result = self.animatronic_ai.update_animatronics(
            self.animatronics, current_time, self.current_night,
            self.left_door_closed, self.right_door_closed, self.camera_system.current_view
        )
        
        # Handle AI result (jumpscare)
        if result == "jumpscare":
            # Find the animatronic that caused the jumpscare
            for animatronic in self.animatronics:
                if animatronic.current_location == Location.OFFICE:
                    self.trigger_jumpscare(animatronic)
                    break
    
    def trigger_jumpscare(self, animatronic):
        """Trigger a jumpscare with enhanced effects."""
        if random.random() < animatronic.jumscare_chance:
            self.jumpscare_active = True
            self.jumpscare_timer = 3.0
            self.flash_effect = True
            self.flash_timer = 0.5
            self.screen_shake = True
            self.shake_timer = 1.0
            self.total_jumpscares += 1
            self.game_state = GameState.GAME_OVER
    
    def update_visual_effects(self, dt):
        """Update visual effects like flashing and screen shake."""
        if self.flash_effect:
            self.flash_timer -= dt
            if self.flash_timer <= 0:
                self.flash_effect = False
        
        if self.screen_shake:
            self.shake_timer -= dt
            if self.shake_timer <= 0:
                self.screen_shake = False
        
        # Update camera static
        self.camera_system.update_static(dt)
    
    def calculate_survival_bonus(self):
        """Calculate enhanced survival bonus and update statistics."""
        power_bonus = int(self.current_power * 10)
        time_bonus = int((6 - self.current_hour) * 100)
        self.survival_bonus = power_bonus + time_bonus + (self.current_night * 100)
        
        # Update statistics
        self.nights_survived += 1
        self.total_score += self.survival_bonus
        
        # Update best survival time
        survival_time = (self.current_hour - 12) * 60 + self.current_minute
        if survival_time > self.best_survival_time:
            self.best_survival_time = survival_time
    
    def draw_office(self):
        """Draw the office with enhanced visual effects."""
        # Apply screen shake
        shake_offset = 0
        if self.screen_shake:
            shake_offset = random.randint(-5, 5)
        
        self.screen.fill(DARK_GRAY)
        
        # Office background
        office_rect = pygame.Rect(100 + shake_offset, 100, 1000, 500)
        pygame.draw.rect(self.screen, BLACK, office_rect)
        
        # Doors with enhanced visuals
        left_door_rect = pygame.Rect(100 + shake_offset, 100, 200, 500)
        right_door_rect = pygame.Rect(900 + shake_offset, 100, 200, 500)
        
        if self.left_door_closed:
            pygame.draw.rect(self.screen, RED, left_door_rect)
            pygame.draw.circle(self.screen, YELLOW, (150 + shake_offset, 120), 10)
        else:
            pygame.draw.rect(self.screen, GRAY, left_door_rect)
        
        if self.right_door_closed:
            pygame.draw.rect(self.screen, RED, right_door_rect)
            pygame.draw.circle(self.screen, YELLOW, (1050 + shake_offset, 120), 10)
        else:
            pygame.draw.rect(self.screen, GRAY, right_door_rect)
        
        # Enhanced lights
        if self.left_light_on:
            light_rect = pygame.Rect(50 + shake_offset, 150, 50, 400)
            pygame.draw.rect(self.screen, YELLOW, light_rect)
            pygame.draw.polygon(self.screen, (255, 255, 200, 100), 
                              [(50 + shake_offset, 150), (0, 200), (0, 500), (50 + shake_offset, 550)])
        
        if self.right_light_on:
            light_rect = pygame.Rect(1100 + shake_offset, 150, 50, 400)
            pygame.draw.rect(self.screen, YELLOW, light_rect)
            pygame.draw.polygon(self.screen, (255, 255, 200, 100), 
                              [(1100 + shake_offset, 150), (1200, 200), (1200, 500), (1100 + shake_offset, 550)])
        
        # Animatronics in office
        for animatronic in self.animatronics:
            if animatronic.current_location == Location.OFFICE:
                self.draw_animatronic(animatronic, shake_offset)
        
        # Flash effect
        if self.flash_effect:
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surface.set_alpha(128)
            flash_surface.fill(WHITE)
            self.screen.blit(flash_surface, (0, 0))
    
    def draw_camera_view(self):
        """Draw the enhanced camera view."""
        self.screen.fill(BLACK)
        
        # Camera static effect
        if self.camera_system.camera_static:
            for _ in range(150):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                pygame.draw.circle(self.screen, WHITE, (x, y), 1)
        
        # Camera view background with scan lines effect
        camera_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 200)
        pygame.draw.rect(self.screen, DARK_GRAY, camera_rect)
        
        # Scan lines effect
        for y in range(50, SCREEN_HEIGHT - 150, 4):
            pygame.draw.line(self.screen, (0, 0, 0, 50), (50, y), (SCREEN_WIDTH - 50, y), 1)
        
        # Show animatronics in current camera view
        for animatronic in self.animatronics:
            if animatronic.current_location.value == self.camera_system.current_view.value:
                self.draw_animatronic(animatronic)
        
        # Enhanced camera label with glow effect
        font = pygame.font.Font(None, 36)
        label = font.render(f"Camera: {self.camera_system.current_view.value}", True, WHITE)
        label_rect = label.get_rect(center=(SCREEN_WIDTH // 2, 30))
        
        # Glow effect
        glow_surface = font.render(f"Camera: {self.camera_system.current_view.value}", True, (100, 100, 100))
        glow_rect = glow_surface.get_rect(center=(SCREEN_WIDTH // 2 + 2, 32))
        self.screen.blit(glow_surface, glow_rect)
        
        self.screen.blit(label, label_rect)
        
        # Camera status indicator
        small_font = pygame.font.Font(None, 24)
        status_text = small_font.render("LIVE", True, RED)
        self.screen.blit(status_text, (SCREEN_WIDTH - 100, 20))
        
        # Watching indicator
        watching_animatronics = [a for a in self.animatronics if a.is_being_watched]
        if watching_animatronics:
            watch_text = small_font.render(f"Watching: {len(watching_animatronics)} animatronic(s) stopped", True, GREEN)
            self.screen.blit(watch_text, (50, 80))
    
    def draw_animatronic(self, animatronic, shake_offset=0):
        """Draw an animatronic with enhanced visuals."""
        colors = {
            AnimatronicType.FREDDY: BROWN,
            AnimatronicType.BONNIE: BLUE,
            AnimatronicType.CHICA: YELLOW,
            AnimatronicType.FOXY: ORANGE,
            AnimatronicType.GOLDEN_FREDDY: GOLD
        }
        
        color = colors.get(animatronic.name, WHITE)
        
        # Position based on location with new room structure
        if animatronic.current_location == Location.OFFICE:
            rect = pygame.Rect(400 + shake_offset, 200, 100, 150)
        else:
            # Updated positions for new room structure
            positions = {
                # Starting areas (far from office)
                Location.STAGE: (200, 300),
                Location.BACKSTAGE: (400, 300),
                Location.SUPPLY_CLOSET: (600, 300),
                
                # Intermediate areas
                Location.DINING_AREA: (800, 300),
                Location.KITCHEN: (200, 400),
                Location.BATHROOM: (400, 400),
                Location.STORAGE_ROOM: (600, 400),
                
                # Approach areas (closer to office)
                Location.HALLWAY_LEFT: (800, 400),
                Location.HALLWAY_RIGHT: (200, 500),
                Location.VENT_LEFT: (400, 500),
                Location.VENT_RIGHT: (600, 500),
            }
            pos = positions.get(animatronic.current_location, (500, 300))
            rect = pygame.Rect(pos[0] + shake_offset, pos[1], 80, 120)
        
        # Draw animatronic body
        pygame.draw.rect(self.screen, color, rect)
        
        # Add details based on animatronic type
        if animatronic.name == AnimatronicType.FREDDY:
            # Hat
            hat_rect = pygame.Rect(rect.x - 10, rect.y - 20, 120, 20)
            pygame.draw.rect(self.screen, BROWN, hat_rect)
            # Bow tie
            bow_rect = pygame.Rect(rect.x + 35, rect.y + 40, 30, 15)
            pygame.draw.rect(self.screen, RED, bow_rect)
        
        # Eyes (glowing effect)
        eye_color = (255, 255, 255) if animatronic.current_location == Location.OFFICE else (255, 0, 0)
        pygame.draw.circle(self.screen, eye_color, (rect.x + 25, rect.y + 30), 8)
        pygame.draw.circle(self.screen, eye_color, (rect.x + 75, rect.y + 30), 8)
        
        # Watching indicator
        if animatronic.is_being_watched:
            # Draw a green border around watched animatronics
            pygame.draw.rect(self.screen, GREEN, rect, 3)
            # Add "WATCHED" text
            small_font = pygame.font.Font(None, 20)
            watched_text = small_font.render("WATCHED", True, GREEN)
            self.screen.blit(watched_text, (rect.x, rect.y - 35))
        
        # Name label
        small_font = pygame.font.Font(None, 24)
        name_text = small_font.render(animatronic.name.value, True, WHITE)
        self.screen.blit(name_text, (rect.x, rect.y - 20))
    
    def draw_menu(self):
        """Draw the enhanced main menu."""
        self.screen.fill(BLACK)
        
        # Animated background effect
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(self.screen, DARK_GRAY, (x, y), 2)
        
        # Title with glow effect
        title = self.ui_system.large_font.render("Five Nights at Freddy's Enhanced", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        
        # Glow effect
        for offset in range(3):
            glow_surface = self.ui_system.large_font.render("Five Nights at Freddy's Enhanced", True, (100, 0, 0))
            glow_rect = glow_surface.get_rect(center=(SCREEN_WIDTH // 2 + offset, 150 + offset))
            self.screen.blit(glow_surface, glow_rect)
        
        self.screen.blit(title, title_rect)
        
        # Menu buttons
        buttons = [
            ("Start Game", GREEN),
            ("Custom Night", BLUE),
            ("Statistics", YELLOW),
            ("Quit", RED)
        ]
        
        for i, (text, color) in enumerate(buttons):
            button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 250 + i * 60, 200, 50)
            pygame.draw.rect(self.screen, color, button_rect)
            
            button_text = self.ui_system.font.render(text, True, WHITE)
            text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, text_rect)
        
        # Enhanced instructions
        instructions = [
            "Controls: 1/2 - Doors | 3/4 - Lights | C - Camera Map | V - Vent | E - Emergency | TAB - Cycle Cameras",
            "ESC - Return to Office/Pause | Mouse - Click buttons"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.ui_system.small_font.render(instruction, True, WHITE)
            self.screen.blit(text, (50, 500 + i * 25))
    
    def draw_game_over(self):
        """Draw the enhanced game over screen."""
        self.screen.fill(BLACK)
        
        # Animated background with red particles
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(self.screen, (100, 0, 0), (x, y), 2)
        
        # Game over text with dramatic effect
        game_over_text = self.ui_system.large_font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        
        # Glow effect
        for offset in range(5):
            glow_surface = self.ui_system.large_font.render("GAME OVER", True, (50, 0, 0))
            glow_rect = glow_surface.get_rect(center=(SCREEN_WIDTH // 2 + offset, 200 + offset))
            self.screen.blit(glow_surface, glow_rect)
        
        self.screen.blit(game_over_text, text_rect)
        
        # Time survived
        time_text = self.ui_system.font.render(f"Time survived: {self.current_hour:02d}:{self.current_minute:02d}", True, WHITE)
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(time_text, time_rect)
        
        # Power remaining
        power_text = self.ui_system.font.render(f"Power remaining: {int(self.current_power)}%", True, WHITE)
        power_rect = power_text.get_rect(center=(SCREEN_WIDTH // 2, 350))
        self.screen.blit(power_text, power_rect)
        
        # Return button
        restart_text = self.ui_system.font.render("Click to return to menu", True, WHITE)
        restart_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 450, 200, 50)
        pygame.draw.rect(self.screen, GREEN, restart_rect)
        restart_text_rect = restart_text.get_rect(center=restart_rect.center)
        self.screen.blit(restart_text, restart_text_rect)
    
    def draw_victory(self):
        """Draw the enhanced victory screen."""
        self.screen.fill(BLACK)
        
        # Animated background
        for _ in range(100):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(self.screen, GREEN, (x, y), 3)
        
        # Victory text with glow effect
        victory_text = self.ui_system.large_font.render("VICTORY!", True, WHITE)
        text_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        
        # Glow effect
        for offset in range(5):
            glow_surface = self.ui_system.large_font.render("VICTORY!", True, (0, 100, 0))
            glow_rect = glow_surface.get_rect(center=(SCREEN_WIDTH // 2 + offset, 150 + offset))
            self.screen.blit(glow_surface, glow_rect)
        
        self.screen.blit(victory_text, text_rect)
        
        # Survival message
        survival_text = self.ui_system.font.render("You survived the night!", True, WHITE)
        survival_rect = survival_text.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(survival_text, survival_rect)
        
        # Enhanced bonus display
        bonus_text = self.ui_system.font.render(f"Survival Bonus: {self.survival_bonus} points", True, GOLD)
        bonus_rect = bonus_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(bonus_text, bonus_rect)
        
        # Time survived
        time_text = self.ui_system.small_font.render(f"Time survived: {self.current_hour:02d}:{self.current_minute:02d}", True, WHITE)
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, 350))
        self.screen.blit(time_text, time_rect)
        
        # Night progress
        if self.current_night < 5:
            night_text = self.ui_system.small_font.render(f"Night {self.current_night} completed! {5 - self.current_night} nights remaining", True, WHITE)
        else:
            night_text = self.ui_system.small_font.render("All 5 nights completed! You've survived!", True, GOLD)
        night_rect = night_text.get_rect(center=(SCREEN_WIDTH // 2, 380))
        self.screen.blit(night_text, night_rect)
        
        # Action buttons
        if self.current_night < 5:
            # Continue to next night button
            next_night_text = self.ui_system.font.render("Continue to Night " + str(self.current_night + 1), True, WHITE)
            next_night_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 450, 300, 50)
            pygame.draw.rect(self.screen, GREEN, next_night_rect)
            next_night_text_rect = next_night_text.get_rect(center=next_night_rect.center)
            self.screen.blit(next_night_text, next_night_text_rect)
            
            # Return to menu button
            menu_text = self.ui_system.font.render("Return to Menu", True, WHITE)
            menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 520, 200, 50)
            pygame.draw.rect(self.screen, BLUE, menu_rect)
            menu_text_rect = menu_text.get_rect(center=menu_rect.center)
            self.screen.blit(menu_text, menu_text_rect)
        else:
            # Final victory - return to menu
            restart_text = self.ui_system.font.render("Return to Menu", True, WHITE)
            restart_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 450, 200, 50)
            pygame.draw.rect(self.screen, BLUE, restart_rect)
            restart_text_rect = restart_text.get_rect(center=restart_rect.center)
            self.screen.blit(restart_text, restart_text_rect)
    
    def draw_paused(self):
        """Draw the paused screen."""
        # Draw the current game state in background
        if self.camera_system.current_view == CameraView.OFFICE:
            self.draw_office()
        else:
            self.draw_camera_view()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.ui_system.font.render("PAUSED", True, WHITE)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause_text, text_rect)
        
        resume_text = self.ui_system.small_font.render("Press ESC to resume", True, WHITE)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(resume_text, resume_rect)
    
    def draw_statistics(self):
        """Draw the statistics screen."""
        self.screen.fill(BLACK)
        
        # Title
        title = self.ui_system.large_font.render("STATISTICS", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Statistics
        stats = [
            f"Nights Survived: {self.nights_survived}",
            f"Total Score: {self.total_score}",
            f"Total Jumpscares: {self.total_jumpscares}",
            f"Best Survival Time: {self.best_survival_time} minutes",
            f"Current Night: {self.current_night}"
        ]
        
        for i, stat in enumerate(stats):
            text = self.ui_system.font.render(stat, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 50))
            self.screen.blit(text, text_rect)
        
        # Return button
        return_text = self.ui_system.font.render("Press ESC to return", True, WHITE)
        return_rect = return_text.get_rect(center=(SCREEN_WIDTH // 2, 500))
        self.screen.blit(return_text, return_rect)
        
        pygame.display.flip()
    
    def load_statistics(self):
        """Load saved statistics from file."""
        try:
            with open('fnaf_stats.json', 'r') as f:
                data = json.load(f)
                self.nights_survived = data.get('nights_survived', 0)
                self.total_jumpscares = data.get('total_jumpscares', 0)
                self.best_survival_time = data.get('best_survival_time', 0)
                self.total_score = data.get('total_score', 0)
        except FileNotFoundError:
            pass
    
    def save_statistics(self):
        """Save statistics to file."""
        data = {
            'nights_survived': self.nights_survived,
            'total_jumpscares': self.total_jumpscares,
            'best_survival_time': self.best_survival_time,
            'total_score': self.total_score
        }
        with open('fnaf_stats.json', 'w') as f:
            json.dump(data, f)
    
    def update(self, dt):
        """Update game state."""
        if self.game_state == GameState.PLAYING:
            self.update_time()
            self.update_power()
            self.update_animatronics()
            self.update_visual_effects(dt)
            
            # Update jumpscare timer
            if self.jumpscare_active:
                self.jumpscare_timer -= dt
                if self.jumpscare_timer <= 0:
                    self.jumpscare_active = False
    
    def draw(self):
        """Draw the current game state."""
        if self.game_state == GameState.MENU:
            self.draw_menu()
        elif self.game_state == GameState.PLAYING:
            if self.camera_system.current_view == CameraView.OFFICE:
                self.draw_office()
            else:
                self.camera_system.draw_camera_view(self.screen, self.animatronics)
            self.ui_system.draw_ui(
                self.screen, self.current_power, MAX_POWER, self.current_hour, 
                self.current_minute, self.current_night, self.left_door_closed, 
                self.right_door_closed, self.left_light_on, self.right_light_on, 
                self.vent_system_active, self.emergency_power, self.emergency_power_remaining,
                self.camera_system.current_view, self.animatronics, self.animatronic_ai
            )
        elif self.game_state == GameState.GAME_OVER:
            self.draw_game_over()
        elif self.game_state == GameState.VICTORY:
            self.draw_victory()
        elif self.game_state == GameState.PAUSED:
            self.draw_paused()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        running = True
        
        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Convert to seconds
            
            running = self.handle_events()
            self.update(dt)
            self.draw()
        
        self.save_statistics()
        pygame.quit()

if __name__ == "__main__":
    game = FNAFGame()
    game.run() 