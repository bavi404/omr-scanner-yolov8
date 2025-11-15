import os
import json
from omr_processor import OMRProcessor
from glob import glob

# Configuration
MODEL_PATH = r"C:\Users\sanka\runs\detect\train3\weights\best.pt"
TEST_IMAGES_DIR = r"C:\Users\sanka\Downloads\OMR MCQS DATASET.v1i.yolov8\test\images"
OUTPUT_DIR = "batch_results"

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize processor
print("="*60)
print("BATCH OMR PROCESSING")
print("="*60)
processor = OMRProcessor(MODEL_PATH)

# Find all test images
image_files = glob(os.path.join(TEST_IMAGES_DIR, "*.jpg")) + \
              glob(os.path.join(TEST_IMAGES_DIR, "*.png"))

print(f"\nFound {len(image_files)} images to process\n")

# Process each image
results_summary = []

for i, image_path in enumerate(image_files, 1):
    filename = os.path.basename(image_path)
    print(f"[{i}/{len(image_files)}] Processing: {filename}...")
    
    try:
        result = processor.process_omr(image_path, debug=False)
        
        # Save individual result
        output_file = os.path.join(OUTPUT_DIR, f"{os.path.splitext(filename)[0]}.json")
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=4)
        
        # Add to summary
        summary = {
            "filename": filename,
            "name": result.get("name", ""),
            "roll_number": result.get("roll_number", ""),
            "questions_detected": len(result.get("answers", {})),
            "answer_string": result.get("answer_string", ""),
            "status": "✓ Success"
        }
        results_summary.append(summary)
        
        print(f"  ✓ Detected {len(result['answers'])} questions")
        print(f"  ✓ Name: {result['name']}")
        print(f"  ✓ Answers: {result['answer_string'][:30]}...")
        
    except Exception as e:
        print(f"  ✗ ERROR: {str(e)}")
        results_summary.append({
            "filename": filename,
            "status": f"✗ Error: {str(e)}"
        })
    
    print()

# Save summary
summary_file = os.path.join(OUTPUT_DIR, "_summary.json")
with open(summary_file, 'w') as f:
    json.dump(results_summary, f, indent=4)

# Print summary
print("="*60)
print("PROCESSING COMPLETE")
print("="*60)
print(f"\nProcessed: {len(image_files)} images")
print(f"Success: {sum(1 for r in results_summary if '✓' in r['status'])}")
print(f"Errors: {sum(1 for r in results_summary if '✗' in r['status'])}")
print(f"\nResults saved to: {OUTPUT_DIR}/")
print(f"Summary saved to: {summary_file}")

# Statistics
if results_summary:
    questions_detected = [r.get("questions_detected", 0) for r in results_summary if "questions_detected" in r]
    if questions_detected:
        avg_questions = sum(questions_detected) / len(questions_detected)
        print(f"\nAverage questions detected: {avg_questions:.1f}")
        print(f"Min: {min(questions_detected)}, Max: {max(questions_detected)}")

