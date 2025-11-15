import json
import cv2
from omr_processor import OMRProcessor

# -------------------------------------------------------
# --- CONFIGURATION ---
# -------------------------------------------------------
MODEL_PATH = r"C:\Users\sanka\runs\detect\train3\weights\best.pt"
IMAGE_PATH = r"C:\Users\sanka\Downloads\OMR MCQS DATASET.v1i.yolov8\test\images\img41.jpg"
OUTPUT_JSON = "omr_output.json"
SAVE_DEBUG_IMAGE = True  # Set to True to save annotated image

# -------------------------------------------------------
# --- PROCESS OMR ---
# -------------------------------------------------------
print("=" * 60)
print("OMR SHEET PROCESSOR")
print("=" * 60)

# Initialize processor
processor = OMRProcessor(MODEL_PATH)

# Process OMR
print(f"\nProcessing: {IMAGE_PATH}")
result = processor.process_omr(IMAGE_PATH, debug=True)

# Check for errors
if "error" in result:
    print(f"\n❌ ERROR: {result['error']}")
    exit(1)

# -------------------------------------------------------
# --- DISPLAY RESULTS ---
# -------------------------------------------------------
print("\n" + "=" * 60)
print("EXTRACTED INFORMATION")
print("=" * 60)

print(f"\n📝 Name: {result['name']}")
print(f"🔢 Roll Number: {result['roll_number']}")
print(f"📋 Version: {result['version']}")
print(f"✅ Questions Answered: {len(result['answers'])}")

print(f"\n📊 Answer String:")
print(f"   {result['answer_string']}")

if len(result['answers']) > 0:
    print(f"\n📋 Detailed Answers:")
    for i in range(0, len(result['answers']), 10):
        questions = list(result['answers'].items())[i:i+10]
        q_nums = " ".join([f"{q:3s}" for q, _ in questions])
        answers = " ".join([f"{a if a else '-':3s}" for _, a in questions])
        print(f"   {q_nums}")
        print(f"   {answers}")
        print()

# -------------------------------------------------------
# --- SAVE RESULTS ---
# -------------------------------------------------------
# Save to JSON
with open(OUTPUT_JSON, "w") as f:
    json.dump(result, f, indent=4)

print(f"💾 Results saved to: {OUTPUT_JSON}")

# -------------------------------------------------------
# --- SAVE DEBUG IMAGE (OPTIONAL) ---
# -------------------------------------------------------
if SAVE_DEBUG_IMAGE:
    image = cv2.imread(IMAGE_PATH)
    regions = processor.detect_regions(image)
    
    # Draw regions
    colors = {
        "name": (0, 255, 0),      # Green
        "r_number": (255, 0, 0),  # Blue
        "v_number": (0, 255, 255), # Yellow
        "mcqs": (255, 0, 255),    # Magenta
        "m_area": (128, 128, 128) # Gray
    }
    
    for region_name, region_data in regions.items():
        x1, y1, x2, y2 = region_data["box"]
        color = colors.get(region_name, (255, 255, 255))
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(image, region_name, (x1, y1-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    # Detect and draw bubbles in MCQ region
    if "mcqs" in regions:
        bubbles = processor.detect_bubbles_in_region(image, regions["mcqs"]["box"])
        for bubble in bubbles:
            cx, cy = bubble["center"]
            is_filled = bubble["fill_ratio"] > 0.3
            color = (0, 0, 255) if is_filled else (0, 255, 0)  # Red if filled, green if empty
            cv2.circle(image, (cx, cy), 5, color, -1)
    
    output_debug = "omr_debug_annotated.jpg"
    cv2.imwrite(output_debug, image)
    print(f"🖼️  Debug image saved to: {output_debug}")

print("\n" + "=" * 60)
print("✅ PROCESSING COMPLETE!")
print("=" * 60)
