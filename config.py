"""
Configuration file for OMR Sheet Processor
Edit these paths according to your setup
"""

# Model Configuration
MODEL_PATH = r"C:\Users\sanka\runs\detect\train3\weights\best.pt"

# Default Image Path (for test.py)
DEFAULT_IMAGE_PATH = r"C:\Users\sanka\Downloads\OMR MCQS DATASET.v1i.yolov8\test\images\test_img_20.jpg"

# Directories
TEST_IMAGES_DIR = r"C:\Users\sanka\Downloads\OMR MCQS DATASET.v1i.yolov8\test\images"
OUTPUT_DIR = "batch_results"
UPLOAD_FOLDER = "uploads"

# Processing Parameters
DETECTION_CONFIDENCE = 0.25  # YOLO confidence threshold (0-1)
FILL_THRESHOLD = 0.25        # Bubble fill threshold (0-1, lower = more sensitive)

# Bubble Detection Parameters
MIN_BUBBLE_AREA = 20         # Minimum bubble size in pixels²
MAX_BUBBLE_AREA = 1000       # Maximum bubble size in pixels²

# Grouping Parameters
VERTICAL_THRESHOLD = 8       # Max pixels between bubbles in same row
HORIZONTAL_THRESHOLD = 30    # Min pixels between columns/questions

# File Settings
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
SAVE_DEBUG_IMAGES = True     # Save annotated debug images

# Web Server Settings (for app.py)
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000
FLASK_DEBUG = True

