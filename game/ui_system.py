import pygame
from typing import Dict
from .constants import *

class UISystem:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        
        # UI buttons
        self.buttons = self.create_ui_buttons()
    
    def create_ui_buttons(self) -> Dict[str, pygame.Rect]:
        """Create enhanced UI button rectangles."""
        return {
            'left_door': pygame.Rect(50, 650, 100, 50),
            'right_door': pygame.Rect(1050, 650, 100, 50),
            'left_light': pygame.Rect(200, 650, 100, 50),
            'right_light': pygame.Rect(900, 650, 100, 50),
            'camera': pygame.Rect(500, 650, 100, 50),
            'vent': pygame.Rect(400, 650, 100, 50),
            'emergency_power': pygame.Rect(600, 650, 150, 50),
            'settings': pygame.Rect(50, 50, 100, 30),
            'statistics': pygame.Rect(160, 50, 100, 30),
        }
    
    def draw_ui(self, screen, current_power, max_power, current_hour, current_minute, 
                current_night, left_door_closed, right_door_closed, left_light_on, 
                right_light_on, vent_system_active, emergency_power, emergency_power_remaining,
                camera_view, animatronics=None, animatronic_ai=None):
        """Draw the enhanced user interface."""
        # Power meter with warning colors (top left)
        power_rect = pygame.Rect(50, 50, 200, 30)
        pygame.draw.rect(screen, RED, power_rect)
        
        power_percentage = current_power / max_power
        if power_percentage > 0.5:
            power_color = GREEN
        elif power_percentage > 0.2:
            power_color = YELLOW
        else:
            power_color = RED
        
        power_fill_rect = pygame.Rect(50, 50, int(200 * power_percentage), 30)
        pygame.draw.rect(screen, power_color, power_fill_rect)
        
        power_text = self.small_font.render(f"Power left: {int(current_power)}%", True, WHITE)
        screen.blit(power_text, (50, 20))
        
        # Power usage indicators (bottom left) - classic FNAF style
        usage_y = 650
        usage_text = self.small_font.render("Usage:", True, WHITE)
        screen.blit(usage_text, (50, usage_y))
        
        # Usage bars
        bar_width = 15
        bar_height = 30
        bar_spacing = 5
        
        # Left door usage
        if left_door_closed:
            pygame.draw.rect(screen, GREEN, (50, usage_y + 20, bar_width, bar_height))
        else:
            pygame.draw.rect(screen, GRAY, (50, usage_y + 20, bar_width, bar_height))
        
        # Right door usage
        if right_door_closed:
            pygame.draw.rect(screen, GREEN, (50 + bar_width + bar_spacing, usage_y + 20, bar_width, bar_height))
        else:
            pygame.draw.rect(screen, GRAY, (50 + bar_width + bar_spacing, usage_y + 20, bar_width, bar_height))
        
        # Enhanced time display (top center)
        time_text = self.large_font.render(f"{current_hour:02d}:{current_minute:02d}", True, WHITE)
        screen.blit(time_text, (SCREEN_WIDTH // 2 - 80, 20))
        
        # Night display (top right)
        night_text = self.font.render(f"Night {current_night}", True, WHITE)
        screen.blit(night_text, (SCREEN_WIDTH - 150, 20))
        
        # Enhanced control buttons
        button_labels = {
            'left_door': 'Left Door',
            'right_door': 'Right Door',
            'left_light': 'Left Light',
            'right_light': 'Right Light',
            'camera': 'Camera',
            'vent': 'Vent',
            'emergency_power': 'Emergency'
        }
        
        for button_name, button_rect in self.buttons.items():
            if button_name in button_labels:
                color = GREEN if self.is_button_active(button_name, left_door_closed, 
                                                     right_door_closed, left_light_on, 
                                                     right_light_on, vent_system_active, 
                                                     emergency_power) else GRAY
                pygame.draw.rect(screen, color, button_rect)
                
                label = button_labels[button_name]
                text = self.small_font.render(label, True, WHITE)
                text_rect = text.get_rect(center=button_rect.center)
                screen.blit(text, text_rect)
        
        # Enhanced status indicators (bottom center)
        status_y = 720
        statuses = [
            f"Left Door: {'CLOSED' if left_door_closed else 'OPEN'}",
            f"Right Door: {'CLOSED' if right_door_closed else 'OPEN'}",
            f"Left Light: {'ON' if left_light_on else 'OFF'}",
            f"Right Light: {'ON' if right_light_on else 'OFF'}",
            f"Vent System: {'ACTIVE' if vent_system_active else 'INACTIVE'}",
            f"Emergency Power: {'ACTIVE' if emergency_power else 'READY'}"
        ]
        
        for i, status in enumerate(statuses):
            text = self.small_font.render(status, True, WHITE)
            screen.blit(text, (50 + (i % 2) * 300, status_y + (i // 2) * 25))
        
        # Emergency power indicator
        if emergency_power:
            emergency_text = self.font.render(f"EMERGENCY POWER: {int(emergency_power_remaining)}s", True, RED)
            screen.blit(emergency_text, (SCREEN_WIDTH // 2 - 150, 80))
        
        # Camera view indicator
        view_text = self.small_font.render(f"View: {camera_view.value}", True, WHITE)
        screen.blit(view_text, (SCREEN_WIDTH - 200, 80))
        
        # Animatronic danger level indicator
        if animatronics and animatronic_ai:
            danger_levels = []
            for animatronic in animatronics:
                if animatronic.is_active:
                    danger_level = animatronic_ai.get_animatronic_danger_level(animatronic)
                    if danger_level > 2:  # Only show high danger animatronics
                        danger_levels.append(f"{animatronic.name.value}: Level {danger_level}")
            
            if danger_levels:
                danger_text = self.small_font.render("HIGH DANGER: " + ", ".join(danger_levels), True, RED)
                screen.blit(danger_text, (50, 110))
    
    def is_button_active(self, button_name: str, left_door_closed: bool, right_door_closed: bool,
                        left_light_on: bool, right_light_on: bool, vent_system_active: bool,
                        emergency_power: bool) -> bool:
        """Check if a button should be highlighted as active."""
        if button_name == 'left_door':
            return left_door_closed
        elif button_name == 'right_door':
            return right_door_closed
        elif button_name == 'left_light':
            return left_light_on
        elif button_name == 'right_light':
            return right_light_on
        elif button_name == 'vent':
            return vent_system_active
        elif button_name == 'emergency_power':
            return emergency_power
        return False
    
    def handle_button_click(self, pos):
        """Handle button clicks and return the button name."""
        for button_name, button_rect in self.buttons.items():
            if button_rect.collidepoint(pos):
                return button_name
        return None 