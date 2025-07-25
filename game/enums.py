from enum import Enum

class AnimatronicType(Enum):
    FREDDY = "Freddy"
    BONNIE = "Bonnie"
    CHICA = "Chica"
    FOXY = "Foxy"
    GOLDEN_FREDDY = "Golden Freddy"

class Location(Enum):
    # Starting areas (far from office)
    STAGE = "Stage"
    BACKSTAGE = "Backstage"
    SUPPLY_CLOSET = "Supply Closet"
    
    # Intermediate areas
    DINING_AREA = "Dining Area"
    KITCHEN = "Kitchen"
    BATHROOM = "Bathroom"
    STORAGE_ROOM = "Storage Room"
    
    # Approach areas (closer to office)
    HALLWAY_LEFT = "Left Hallway"
    HALLWAY_RIGHT = "Right Hallway"
    VENT_LEFT = "Left Vent"
    VENT_RIGHT = "Right Vent"
    
    # Final destination
    OFFICE = "Office"

class GameState(Enum):
    MENU = "Menu"
    PLAYING = "Playing"
    GAME_OVER = "Game Over"
    VICTORY = "Victory"
    PAUSED = "Paused"
    CAMERA_MAP = "Camera Map"

class CameraView(Enum):
    OFFICE = "Office"
    STAGE = "Stage"
    DINING_AREA = "Dining Area"
    KITCHEN = "Kitchen"
    BACKSTAGE = "Backstage"
    HALLWAY_LEFT = "Left Hallway"
    HALLWAY_RIGHT = "Right Hallway"
    SUPPLY_CLOSET = "Supply Closet"
    BATHROOM = "Bathroom"
    STORAGE_ROOM = "Storage Room"
    VENT_LEFT = "Left Vent"
    VENT_RIGHT = "Right Vent" 