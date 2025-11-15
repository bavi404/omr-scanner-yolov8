import cv2
import numpy as np
import easyocr
from ultralytics import YOLO

class OMRProcessor:
    def __init__(self, model_path):
        """Initialize OMR processor with YOLO model."""
        self.model = YOLO(model_path)
        self.reader = easyocr.Reader(['en'], gpu=False)
        
    def detect_regions(self, image, conf=0.25):
        """Detect OMR regions using YOLO."""
        results = self.model(image, conf=conf)[0]
        regions = {}
        
        for box in results.boxes:
            cls = int(box.cls)
            label = self.model.names[cls]
            confidence = float(box.conf)
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            if label in ["name", "r_number", "v_number", "mcqs", "m_area"]:
                regions[label] = {
                    "box": (x1, y1, x2, y2),
                    "confidence": confidence
                }
        
        return regions
    
    def extract_text(self, image, region_box):
        """Extract text from a region using OCR."""
        x1, y1, x2, y2 = region_box
        crop = image[y1:y2, x1:x2]
        
        # Preprocess for better OCR
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        text = self.reader.readtext(gray, detail=0)
        return " ".join(text).strip()
    
    def detect_bubbles_in_region(self, image, region_box, min_area=20, max_area=1000):
        """Detect circular bubbles in a region using enhanced multi-method detection."""
        x1, y1, x2, y2 = region_box
        roi = image[y1:y2, x1:x2]
        
        # Convert to grayscale
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Try multiple preprocessing methods
        all_bubbles = []
        
        # Method 1: Otsu's thresholding
        blur1 = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh1 = cv2.threshold(blur1, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours1, _ = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Method 2: Adaptive thresholding
        thresh2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 2)
        contours2, _ = cv2.findContours(thresh2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Combine contours from both methods
        all_contours = list(contours1) + list(contours2)
        
        # Store unique bubbles (avoid duplicates)
        seen_positions = set()
        bubbles = []
        
        for cnt in all_contours:
            area = cv2.contourArea(cnt)
            
            # Filter by area
            if min_area < area < max_area:
                # Get bounding box
                bx, by, bw, bh = cv2.boundingRect(cnt)
                
                # Check if roughly circular
                aspect_ratio = float(bw) / bh if bh > 0 else 0
                if 0.4 <= aspect_ratio <= 2.5:  # Very flexible for various shapes
                    # Calculate center
                    cx_rel = bx + bw // 2
                    cy_rel = by + bh // 2
                    cx = x1 + cx_rel
                    cy = y1 + cy_rel
                    
                    # Check for duplicates (bubbles detected by both methods)
                    pos_key = (cx // 5, cy // 5)  # Grid-based deduplication
                    if pos_key in seen_positions:
                        continue
                    seen_positions.add(pos_key)
                    
                    # Calculate fill ratio using Otsu threshold
                    roi_bubble = thresh1[by:by+bh, bx:bx+bw]
                    if roi_bubble.size > 0:
                        filled_pixels = cv2.countNonZero(roi_bubble)
                        total_pixels = bw * bh
                        fill_ratio = filled_pixels / total_pixels if total_pixels > 0 else 0
                    else:
                        fill_ratio = 0
                    
                    bubbles.append({
                        "center": (cx, cy),
                        "box": (x1 + bx, y1 + by, x1 + bx + bw, y1 + by + bh),
                        "area": area,
                        "fill_ratio": fill_ratio
                    })
        
        return bubbles
    
    def group_bubbles_into_questions(self, bubbles, vertical_threshold=8, horizontal_threshold=30):
        """Group bubbles into questions supporting multi-column layouts."""
        if not bubbles:
            return []
        
        # Step 1: Group by Y-coordinate into rows
        sorted_by_y = sorted(bubbles, key=lambda b: b["center"][1])
        
        rows = []
        current_row = [sorted_by_y[0]]
        
        for i in range(1, len(sorted_by_y)):
            prev_y = sorted_by_y[i-1]["center"][1]
            curr_y = sorted_by_y[i]["center"][1]
            
            if abs(curr_y - prev_y) <= vertical_threshold:
                current_row.append(sorted_by_y[i])
            else:
                rows.append(current_row)
                current_row = [sorted_by_y[i]]
        
        rows.append(current_row)
        
        # Step 2: Within each row, group by X-coordinate (handle multiple columns)
        all_questions = []
        
        for row in rows:
            # Sort bubbles in row by X-coordinate
            row_sorted = sorted(row, key=lambda b: b["center"][0])
            
            # Group by X-position to separate columns
            column_groups = []
            current_group = [row_sorted[0]]
            
            for i in range(1, len(row_sorted)):
                prev_x = row_sorted[i-1]["center"][0]
                curr_x = row_sorted[i]["center"][0]
                
                # If X-gap is large, it's a new column/question
                if abs(curr_x - prev_x) > horizontal_threshold:
                    column_groups.append(current_group)
                    current_group = [row_sorted[i]]
                else:
                    current_group.append(row_sorted[i])
            
            column_groups.append(current_group)
            
            # Each column group in a row is a separate question
            for group in column_groups:
                # Sort left to right within question
                group_sorted = sorted(group, key=lambda b: b["center"][0])
                # Only keep groups with 1-8 bubbles (valid question) - be flexible
                if 1 <= len(group_sorted) <= 8:
                    all_questions.append(group_sorted)
        
        return all_questions
    
    def extract_mcq_answers(self, image, mcq_region_box, fill_threshold=0.25, debug=False):
        """Extract MCQ answers from the MCQ region."""
        # Detect bubbles in MCQ region
        bubbles = self.detect_bubbles_in_region(image, mcq_region_box)
        
        if debug:
            print(f"Total bubbles detected: {len(bubbles)}")
        
        if not bubbles:
            return {}
        
        # Group into questions
        questions = self.group_bubbles_into_questions(bubbles)
        
        if debug:
            print(f"Grouped into {len(questions)} questions")
        
        # Extract answers
        answers = {}
        options = ['A', 'B', 'C', 'D', 'E']  # Support up to 5 options
        
        for q_num, question_bubbles in enumerate(questions, start=1):
            # Sort left to right
            question_bubbles.sort(key=lambda b: b["center"][0])
            
            # Find filled bubble
            selected = None
            for idx, bubble in enumerate(question_bubbles):
                if bubble["fill_ratio"] > fill_threshold and idx < len(options):
                    selected = options[idx]
                    break
            
            answers[f"Q{q_num}"] = selected
        
        return answers
    
    def extract_roll_number_bubbles(self, image, roll_region_box, fill_threshold=0.3):
        """Extract roll number from bubble grid (numbers 0-9 in columns)."""
        bubbles = self.detect_bubbles_in_region(image, roll_region_box, min_area=30, max_area=400)
        
        if not bubbles:
            return ""
        
        # Sort bubbles into a grid (columns left to right, rows top to bottom)
        bubbles.sort(key=lambda b: (b["center"][0], b["center"][1]))
        
        # Group into columns
        columns = []
        current_col = [bubbles[0]]
        x_threshold = 30
        
        for i in range(1, len(bubbles)):
            prev_x = bubbles[i-1]["center"][0]
            curr_x = bubbles[i]["center"][0]
            
            if abs(curr_x - prev_x) < x_threshold:
                current_col.append(bubbles[i])
            else:
                columns.append(current_col)
                current_col = [bubbles[i]]
        
        columns.append(current_col)
        
        # Extract digit from each column
        roll_number = ""
        for col in columns:
            col.sort(key=lambda b: b["center"][1])  # Top to bottom
            
            for idx, bubble in enumerate(col):
                if bubble["fill_ratio"] > fill_threshold:
                    roll_number += str(idx)
                    break
        
        return roll_number
    
    def process_omr(self, image_path, debug=False):
        """Process complete OMR sheet and extract all information."""
        # Load image
        image = cv2.imread(image_path)
        
        if image is None:
            return {"error": "Could not load image"}
        
        # Detect regions
        regions = self.detect_regions(image)
        
        if debug:
            print(f"\nDetected regions: {list(regions.keys())}")
        
        result = {
            "name": "",
            "roll_number": "",
            "version": "",
            "answers": {},
            "answer_string": ""
        }
        
        # Extract name
        if "name" in regions:
            result["name"] = self.extract_text(image, regions["name"]["box"])
        
        # Extract version
        if "v_number" in regions:
            result["version"] = self.extract_text(image, regions["v_number"]["box"])
        
        # Extract roll number
        if "r_number" in regions:
            # Try bubble detection first
            roll_from_bubbles = self.extract_roll_number_bubbles(image, regions["r_number"]["box"])
            if roll_from_bubbles:
                result["roll_number"] = roll_from_bubbles
            else:
                # Fallback to OCR
                result["roll_number"] = self.extract_text(image, regions["r_number"]["box"])
        
        # Extract MCQ answers - prefer m_area over mcqs as it's usually larger
        mcq_region_to_use = None
        if "m_area" in regions:
            mcq_region_to_use = regions["m_area"]["box"]
            if debug:
                print("Using m_area for bubble detection (larger region)")
        elif "mcqs" in regions:
            mcq_region_to_use = regions["mcqs"]["box"]
            if debug:
                print("Using mcqs for bubble detection")
        
        if mcq_region_to_use:
            result["answers"] = self.extract_mcq_answers(image, mcq_region_to_use)
            
            # Create answer string (e.g., "ABCDABCD...")
            sorted_questions = sorted(result["answers"].items(), 
                                    key=lambda x: int(x[0].replace('Q', '')))
            result["answer_string"] = "".join([ans if ans else "-" for _, ans in sorted_questions])
        
        if debug:
            print(f"Name: {result['name']}")
            print(f"Roll Number: {result['roll_number']}")
            print(f"Version: {result['version']}")
            print(f"Total Questions: {len(result['answers'])}")
            print(f"Answer String: {result['answer_string']}")
        
        return result

