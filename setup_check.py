"""
Setup verification script
Run this to check if everything is properly configured
"""

import os
import sys

def check_dependencies():
    """Check if all required packages are installed"""
    print("Checking dependencies...")
    required = ['cv2', 'numpy', 'ultralytics', 'easyocr', 'flask']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing.append(package)
    
    return len(missing) == 0

def check_model():
    """Check if model file exists"""
    print("\nChecking model file...")
    from config import MODEL_PATH
    
    if os.path.exists(MODEL_PATH):
        size_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)
        print(f"  ✓ Model found: {MODEL_PATH}")
        print(f"  ✓ Size: {size_mb:.2f} MB")
        return True
    else:
        print(f"  ✗ Model NOT found at: {MODEL_PATH}")
        print("  → Place your trained YOLOv8 model at the specified path")
        return False

def check_directories():
    """Check if required directories exist"""
    print("\nChecking directories...")
    from config import TEST_IMAGES_DIR, OUTPUT_DIR, UPLOAD_FOLDER
    
    dirs_ok = True
    
    # Check test images
    if os.path.exists(TEST_IMAGES_DIR):
        num_images = len([f for f in os.listdir(TEST_IMAGES_DIR) 
                         if f.endswith(('.jpg', '.png', '.jpeg'))])
        print(f"  ✓ Test images directory: {num_images} images found")
    else:
        print(f"  ⚠ Test images directory not found (optional)")
    
    # Create output directories if they don't exist
    for dir_name, dir_path in [("Output", OUTPUT_DIR), ("Upload", UPLOAD_FOLDER)]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"  ✓ Created {dir_name} directory: {dir_path}")
        else:
            print(f"  ✓ {dir_name} directory exists")
    
    return True

def check_config():
    """Check if config file is accessible"""
    print("\nChecking configuration...")
    try:
        import config
        print(f"  ✓ config.py loaded")
        print(f"  ✓ Model path: {config.MODEL_PATH}")
        print(f"  ✓ Detection confidence: {config.DETECTION_CONFIDENCE}")
        print(f"  ✓ Fill threshold: {config.FILL_THRESHOLD}")
        return True
    except Exception as e:
        print(f"  ✗ Error loading config: {e}")
        return False

def main():
    print("="*60)
    print("OMR SHEET PROCESSOR - SETUP VERIFICATION")
    print("="*60)
    print()
    
    checks = {
        "Dependencies": check_dependencies(),
        "Configuration": check_config(),
        "Model File": check_model(),
        "Directories": check_directories()
    }
    
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    all_passed = True
    for check_name, passed in checks.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{check_name:20s} {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 All checks passed! You're ready to process OMR sheets.")
        print("\nQuick start:")
        print("  python test.py          - Process single image")
        print("  python app.py           - Start web interface")
        print("  python batch_process.py - Batch processing")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nTo install missing dependencies:")
        print("  pip install -r requirements.txt")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

