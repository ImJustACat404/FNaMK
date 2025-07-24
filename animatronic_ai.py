import random
import time
from typing import List, Optional
from .enums import AnimatronicType, Location, CameraView
from .animatronic import Animatronic
from .constants import WATCHING_STOP_DURATION, WATCHING_DISTANCE

class AnimatronicAI:
    def __init__(self):
        # Movement paths for each animatronic (structured progression)
        self.movement_paths = {
            AnimatronicType.FREDDY: [
                Location.STAGE,
                Location.DINING_AREA,
                Location.STORAGE_ROOM,
                Location.HALLWAY_LEFT,
                Location.VENT_LEFT,
                Location.OFFICE
            ],
            AnimatronicType.BONNIE: [
                Location.STAGE,
                Location.DINING_AREA,
                Location.KITCHEN,
                Location.HALLWAY_RIGHT,
                Location.OFFICE
            ],
            AnimatronicType.CHICA: [
                Location.STAGE,
                Location.DINING_AREA,
                Location.KITCHEN,
                Location.HALLWAY_RIGHT,
                Location.OFFICE
            ],
            AnimatronicType.FOXY: [
                Location.BACKSTAGE,
                Location.SUPPLY_CLOSET,
                Location.STORAGE_ROOM,
                Location.HALLWAY_LEFT,
                Location.OFFICE
            ],
            AnimatronicType.GOLDEN_FREDDY: [
                Location.SUPPLY_CLOSET,
                Location.BATHROOM,
                Location.STORAGE_ROOM,
                Location.VENT_RIGHT,
                Location.OFFICE
            ]
        }
    
    def update_animatronics(self, animatronics: List[Animatronic], current_time: float, 
                          current_night: int, left_door_closed: bool, right_door_closed: bool,
                          camera_view) -> Optional[str]:
        """Update all animatronics with much slower movement and night-based scaling."""
        
        # Much slower base movement - significantly reduced for first night
        base_movement_chance = 0.02  # 2% chance per update (was much higher)
        
        # Night-based scaling - starts very slow, increases gradually
        night_multiplier = 1.0 + (current_night - 1) * 0.3  # 30% increase per night
        
        # Calculate final movement chance
        movement_chance = base_movement_chance * night_multiplier
        
        # Cap maximum speed to prevent it from becoming too fast
        movement_chance = min(movement_chance, 0.08)  # Max 8% chance even on night 5
        
        for animatronic in animatronics:
            if not animatronic.is_active:
                continue
            
            # Check if animatronic is being watched
            is_watched = self.is_animatronic_being_watched(animatronic, camera_view)
            animatronic.update_watching_status(is_watched, current_time)
            
            # Only move if not being watched and cooldown is ready
            if animatronic.can_move(current_time) and random.random() < movement_chance:
                result = self.move_animatronic_structured(animatronic, left_door_closed, right_door_closed)
                if result:
                    return result
        
        return None
    
    def get_movement_cooldown(self, location: Location) -> float:
        """Get movement cooldown based on location (much longer cooldowns)."""
        # Much longer cooldowns for slower movement
        if location in [Location.STAGE, Location.BACKSTAGE, Location.SUPPLY_CLOSET]:
            return random.uniform(15.0, 25.0)  # 15-25 seconds in starting areas
        elif location in [Location.DINING_AREA, Location.KITCHEN, Location.BATHROOM, Location.STORAGE_ROOM]:
            return random.uniform(12.0, 20.0)  # 12-20 seconds in intermediate areas
        elif location in [Location.HALLWAY_LEFT, Location.HALLWAY_RIGHT]:
            return random.uniform(8.0, 15.0)  # 8-15 seconds in approach areas
        elif location in [Location.VENT_LEFT, Location.VENT_RIGHT]:
            return random.uniform(5.0, 10.0)  # 5-10 seconds in vents
        else:
            return random.uniform(10.0, 18.0)  # Default cooldown
    
    def is_animatronic_being_watched(self, animatronic: Animatronic, camera_view) -> bool:
        """Check if animatronic is being watched in current camera view."""
        if camera_view == CameraView.OFFICE:
            return False
        
        # Check if animatronic is in current camera view
        if animatronic.current_location.value == camera_view.value:
            return True
        
        # Check nearby locations (adjacent rooms)
        nearby_locations = self.get_nearby_locations(camera_view)
        return animatronic.current_location in nearby_locations
    
    def get_nearby_locations(self, camera_view):
        """Get locations that are adjacent to the current camera view."""
        nearby_map = {
            CameraView.STAGE: [Location.BACKSTAGE, Location.DINING_AREA],
            CameraView.BACKSTAGE: [Location.STAGE, Location.SUPPLY_CLOSET],
            CameraView.SUPPLY_CLOSET: [Location.BACKSTAGE, Location.BATHROOM],
            CameraView.DINING_AREA: [Location.STAGE, Location.KITCHEN, Location.STORAGE_ROOM],
            CameraView.KITCHEN: [Location.DINING_AREA, Location.HALLWAY_RIGHT],
            CameraView.BATHROOM: [Location.SUPPLY_CLOSET, Location.STORAGE_ROOM],
            CameraView.STORAGE_ROOM: [Location.DINING_AREA, Location.BATHROOM, Location.HALLWAY_LEFT, Location.HALLWAY_RIGHT],
            CameraView.HALLWAY_LEFT: [Location.STORAGE_ROOM, Location.VENT_LEFT, Location.OFFICE],
            CameraView.HALLWAY_RIGHT: [Location.STORAGE_ROOM, Location.KITCHEN, Location.OFFICE],
            CameraView.VENT_LEFT: [Location.HALLWAY_LEFT, Location.OFFICE],
            CameraView.VENT_RIGHT: [Location.OFFICE],
        }
        return nearby_map.get(camera_view, [])
    
    def move_animatronic_structured(self, animatronic: Animatronic, left_door_closed: bool, 
                                  right_door_closed: bool) -> Optional[str]:
        """Move animatronic along their structured path."""
        path = self.movement_paths.get(animatronic.name, [])
        if not path:
            return None
        
        current_index = -1
        for i, location in enumerate(path):
            if location == animatronic.current_location:
                current_index = i
                break
        
        if current_index == -1:
            # Animatronic not in their path, reset to start
            animatronic.current_location = path[0]
            return None
        
        # Try to move to next location in path
        if current_index + 1 < len(path):
            next_location = path[current_index + 1]
            
            # Check if movement is blocked
            if not self.can_move_to_location(animatronic, next_location, left_door_closed, right_door_closed):
                # Handle blocked movement
                return self.handle_blocked_movement(animatronic, path, current_index, left_door_closed, right_door_closed)
            
            # Move to next location
            animatronic.current_location = next_location
            animatronic.move_cooldown = self.get_movement_cooldown(next_location)
            
            # Check for jumpscare
            if next_location == Location.OFFICE:
                return "jumpscare"
        
        return None
    
    def can_move_to_location(self, animatronic: Animatronic, target_location: Location,
                           left_door_closed: bool, right_door_closed: bool) -> bool:
        """Check if animatronic can move to target location."""
        # Check if doors block the path
        if target_location == Location.OFFICE:
            if animatronic.name in [AnimatronicType.FREDDY, AnimatronicType.FOXY]:
                return not left_door_closed
            elif animatronic.name in [AnimatronicType.BONNIE, AnimatronicType.CHICA]:
                return not right_door_closed
            elif animatronic.name == AnimatronicType.GOLDEN_FREDDY:
                # Golden Freddy can pass through doors
                return True
        
        return True
    
    def handle_blocked_movement(self, animatronic: Animatronic, path: List[Location], 
                              current_index: int, left_door_closed: bool, right_door_closed: bool) -> Optional[str]:
        """Handle movement when path is blocked."""
        # Return to previous location or random safe spot
        if current_index > 0:
            # Go back one step
            animatronic.current_location = path[current_index - 1]
        else:
            # Return to starting location
            animatronic.current_location = path[0]
        
        animatronic.move_cooldown = self.get_movement_cooldown(animatronic.current_location)
        return None
    
    def get_animatronic_danger_level(self, animatronic: Animatronic) -> int:
        """Get animatronic's danger level based on their position in the path."""
        path = self.movement_paths.get(animatronic.name, [])
        if not path:
            return 0
        
        try:
            current_index = path.index(animatronic.current_location)
            return current_index
        except ValueError:
            return 0 