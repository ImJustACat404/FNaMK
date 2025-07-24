import pygame

# Screen Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)

# Game Settings
TIME_PER_HOUR = 540  # 9 minutes per hour in game (6 hours = 54 minutes total)
MAX_POWER = 200  # Increased from 100 to 200 for stronger battery
POWER_DRAIN_RATE = 0.3  # Reduced from 0.5 to 0.3 for slower drain
DOOR_POWER_COST = 1.5  # Reduced from 2 to 1.5
LIGHT_POWER_COST = 0.8  # Reduced from 1 to 0.8
VENT_POWER_COST = 0.3  # Reduced from 0.5 to 0.3

# Watching Mechanics
WATCHING_STOP_DURATION = 3.0  # How long animatronics stay still when watched
WATCHING_DISTANCE = 2  # How many rooms away they can be watched from

# Game Functionality
VENT_SYSTEM_EFFECTIVENESS = 0.7  # How effective vent system is at blocking animatronics
EMERGENCY_POWER_DURATION = 30  # Seconds of emergency power
POWER_WARNING_THRESHOLD = 40  # Percentage when power warnings start
ANIMATRONIC_AGGRESSION_SCALING = 0.15  # How much aggression increases per night 