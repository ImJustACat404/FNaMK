from dataclasses import dataclass
from typing import List
from .enums import AnimatronicType, Location

@dataclass
class Animatronic:
    name: AnimatronicType
    current_location: Location
    target_location: Location
    movement_speed: float
    aggression: float
    jumscare_chance: float
    is_active: bool = True
    last_move_time: float = 0
    move_cooldown: float = 0
    is_being_watched: bool = False
    watching_timer: float = 0
    last_seen_location: Location = None
    
    def __post_init__(self):
        self.locations = list(Location)
        self.locations.remove(Location.OFFICE)  # Animatronics can't be in office unless jumpscaring
        self.last_seen_location = self.current_location
    
    def update_watching_status(self, is_watched: bool, current_time: float):
        """Update whether the animatronic is being watched."""
        if is_watched:
            self.is_being_watched = True
            self.watching_timer = current_time
            self.last_seen_location = self.current_location
        else:
            # Check if enough time has passed since being watched
            if current_time - self.watching_timer > 3.0:  # 3 seconds after being watched
                self.is_being_watched = False
    
    def can_move(self, current_time: float) -> bool:
        """Check if the animatronic can move (not being watched)."""
        return not self.is_being_watched and current_time - self.last_move_time >= self.move_cooldown 