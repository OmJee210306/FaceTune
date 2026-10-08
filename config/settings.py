import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
SONGS_DIR = os.path.join(BASE_DIR, "songs")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
MODELS_DIR = os.path.join(BASE_DIR, "models")
DB_PATH = os.path.join(BASE_DIR, "database", "facetune.db")
EMBEDDINGS_PATH = os.path.join(MODELS_DIR, "embeddings.pkl")

# Recognition
DEFAULT_THRESHOLD = 0.50
RECOGNITION_STABLE_SECONDS = 1.0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Camera
DEFAULT_CAMERA_INDEX = 0

# GUI
APP_TITLE = "FaceTune"
APP_GEOMETRY = "1200x750"
THEME = "dark"
COLOR_THEME = "blue"

# Appearance
ACCENT_COLOR = "#7B61FF"
BG_DARK = "#0D0D0D"
BG_CARD = "#1A1A2E"
BG_SURFACE = "#16213E"
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#A0A0B0"
SUCCESS_COLOR = "#00E676"
ERROR_COLOR = "#FF5252"
WARNING_COLOR = "#FFD740"

for d in [DATASET_DIR, SONGS_DIR, LOGS_DIR, MODELS_DIR]:
    os.makedirs(d, exist_ok=True)
