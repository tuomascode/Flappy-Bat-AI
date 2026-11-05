import pathlib

PROJECT_ROOT = pathlib.Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"

# --- Game constants ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
TOWER_WIDTH = 50
TOWER_MOVE_SPEED = 3
TOWER_SPACING = 200
TOWER_GAP_MAX = 325
TOWER_GAP_MIN = 135
TOWER_BOUNDARY = 30
TOWER_DIFFICULTY_RATE = 10   # frames per 1 px gap reduction (lower = harder faster)
ACCEL_SCALE = 0.025
POPULATION_SIZE = 100
STAGNATION_LIMIT = 10
