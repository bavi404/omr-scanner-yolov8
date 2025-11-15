# 📝 OMR Sheet Processor

AI-powered Optical Mark Recognition (OMR) system for automated answer sheet processing. Detects and extracts student information and MCQ answers from scanned OMR sheets.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF)](https://github.com/ultralytics/ultralytics)
[![Flask](https://img.shields.io/badge/Flask-2.3%2B-green)](https://flask.palletsprojects.com/)

## ✨ Features

- 🎯 **High Accuracy**: ~88% detection rate on multi-column OMR sheets
- 🔍 **Multi-Column Support**: Handles 1 or 2-column question layouts
- 📊 **Answer String Generation**: Exports answers as a single string (e.g., `ABCDABCD...`)
- 👤 **Student Info Extraction**: Detects name, roll number, and test version
- 🌐 **Web Interface**: Beautiful Flask-based UI for easy uploads
- ⚡ **Fast Processing**: ~200ms per sheet on CPU
- 📦 **Batch Processing**: Process multiple sheets at once
- 🔧 **Flexible**: Adapts to various OMR formats

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/omr-sheet-processor.git
cd omr-sheet-processor

# Install dependencies
pip install -r requirements.txt
```

### Download Model

You'll need a trained YOLOv8 model. Place your `best.pt` model file in:
```
runs/detect/train3/weights/best.pt
```

### Run the Processor

**Option 1: Command Line**
```bash
python test.py
```

**Option 2: Web Interface**
```bash
python app.py
# Open http://localhost:5000 in your browser
```

**Option 3: Batch Processing**
```bash
python batch_process.py
```

## 📖 Usage

### Single Image Processing

```python
from omr_processor import OMRProcessor

# Initialize processor
processor = OMRProcessor(model_path="path/to/best.pt")

# Process OMR sheet
result = processor.process_omr("path/to/omr_image.jpg")

# Get results
print(f"Name: {result['name']}")
print(f"Roll Number: {result['roll_number']}")
print(f"Answer String: {result['answer_string']}")
```

### Output Format

```json
{
    "name": "John Doe",
    "roll_number": "123456",
    "version": "A",
    "answers": {
        "Q1": "B",
        "Q2": "A",
        "Q3": "C",
        ...
    },
    "answer_string": "BACDA..."
}
```

## 🛠️ How It Works

1. **Region Detection**: YOLOv8 detects major regions (name, roll number, MCQ area)
2. **Bubble Detection**: Computer vision finds individual answer bubbles
3. **Multi-Method Thresholding**: Otsu + Adaptive thresholding for robustness
4. **Intelligent Grouping**: Handles multi-column layouts automatically
5. **Fill Detection**: Analyzes fill ratio to determine marked answers
6. **OCR Extraction**: EasyOCR extracts text from name/number fields

## 📁 Project Structure

```
omr-sheet-processor/
├── omr_processor.py      # Core processing engine
├── test.py               # CLI processor
├── app.py                # Flask web application
├── batch_process.py      # Batch processing utility
├── requirements.txt      # Python dependencies
├── data.yaml            # YOLO model configuration
└── README.md            # This file
```

## ⚙️ Configuration

Edit parameters in `omr_processor.py` to fine-tune for your OMR format:

```python
# Bubble Detection
min_area = 20              # Minimum bubble size (pixels²)
max_area = 1000            # Maximum bubble size (pixels²)

# Grouping
vertical_threshold = 8     # Row separation (pixels)
horizontal_threshold = 30  # Column separation (pixels)

# Answer Detection
fill_threshold = 0.25      # Marked bubble threshold (0-1)
```

## 📊 Model Training

The system requires a YOLOv8 model trained to detect:

- `m_area` - Marking area
- `mcqs` - MCQ region
- `name` - Name field
- `r_number` - Roll number field
- `v_number` - Version field

Classes defined in `data.yaml`:
```yaml
names:
  - m_area
  - mcqs
  - name
  - r_number
  - v_number
  - bubble_empty
  - bubble_filled
```

> **Note**: Individual bubbles are detected using computer vision (contour detection), not the YOLO model.

## 🎯 Performance

- **Detection Rate**: 88% (44/50 questions on test dataset)
- **Processing Speed**: ~200ms per image (CPU)
- **Accuracy**: High accuracy on detected bubbles
- **Supported Formats**: JPG, PNG, JPEG

## 🔧 Troubleshooting

### Few Questions Detected

Adjust detection parameters:
```python
min_area = 20      # Lower for smaller bubbles
max_area = 1000    # Raise for larger bubbles
```

### Wrong Answers

Adjust fill threshold:
```python
fill_threshold = 0.25  # Lower = more sensitive
```

### OCR Issues

- Ensure good image contrast
- Use high-resolution scans (600 DPI recommended)
- Check if regions are detected correctly

## 📋 Requirements

- Python 3.8+
- OpenCV
- Ultralytics YOLOv8
- EasyOCR
- Flask
- NumPy

See `requirements.txt` for complete list.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) for object detection
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) for text recognition
- [OpenCV](https://opencv.org/) for image processing

## 📧 Contact

For questions or issues, please open an issue on GitHub.

---

**Made with ❤️ for automated OMR processing**

