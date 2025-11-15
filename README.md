# OMR Scanner - YOLOv8

AI-powered OMR (Optical Mark Recognition) sheet scanner using YOLOv8 for automated answer sheet processing.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF.svg)](https://github.com/ultralytics/ultralytics)
[![Flask](https://img.shields.io/badge/Flask-REST%20API-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

-  **YOLOv8 Detection** - Detects OMR regions (name, roll number, MCQ area)
- **Computer Vision** - Advanced bubble detection and fill analysis
- **Answer Extraction** - Generates answer strings (e.g., `ABCDABCD...`)
- **Student Info** - Extracts name, roll number, test version via OCR
- **REST API** - Easy website integration with CORS support
- **Batch Processing** - Process multiple OMR sheets simultaneously
- **Web Interface** - Beautiful drag & drop UI
- **Production Ready** - Deployment guides for cloud platforms

## Performance

- **Detection Rate**: ~88% (44/50 questions on test images)
- **Processing Speed**: ~200ms per image (CPU)
- **Accuracy**: High accuracy on detected bubbles
- **Multi-Column Support**: Handles 2-column OMR layouts

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/bavi404/omr-scanner-yolov8.git
cd omr-scanner-yolov8
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Download Model Weights

** Model weights not included in repository (too large for GitHub)**

Download the trained YOLOv8 model (`best.pt`) from:
- [Google Drive Link](#) - *(Replace with your link)*
- [Hugging Face](#) - *(Or upload to Hugging Face)*

Place `best.pt` in the project root directory.

### 4. Run API Server

```bash
python api_server.py
```

API will be available at: `http://localhost:5000`

##  Usage Examples

### Option 1: Web Interface

```bash
# Start web UI
python app.py
```

Open `http://localhost:5000` in your browser and upload OMR images.

### Option 2: Command Line

```bash
# Process single image
python test.py
```

Edit `test.py` to change the input image path.

### Option 3: REST API

```bash
# Upload via cURL
curl -X POST -F "file=@omr_sheet.jpg" http://localhost:5000/api/process
```

### Option 4: Batch Processing

```bash
# Process multiple images
python batch_process.py
```

## Website Integration

Integrate with any website using JavaScript:

```javascript
async function processOMR(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('http://your-api-url.com/api/process', {
        method: 'POST',
        body: formData
    });
    
    const data = await response.json();
    console.log('Name:', data.name);
    console.log('Roll Number:', data.roll_number);
    console.log('Answers:', data.answer_string);
}
```

See `frontend_example.html` for complete integration example.

##  API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/process` | POST | Process single OMR sheet |
| `/api/batch` | POST | Process multiple OMR sheets |
| `/api/validate` | POST | Validate answers against key |
| `/api/model-info` | GET | Get model information |

## 📤 API Response Format

```json
{
    "name": "John Doe",
    "roll_number": "12345",
    "version": "A",
    "answers": {
        "Q1": "A",
        "Q2": "B",
        "Q3": "C",
        ...
    },
    "answer_string": "ABCD...",
    "metadata": {
        "questions_detected": 50,
        "processing_status": "success"
    }
}
```

## Architecture

```
┌─────────────────┐
│   OMR Image     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ YOLOv8 Detection│  ← Detects regions (name, roll, MCQ area)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Contour Detection│  ← Finds individual bubbles
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Fill Analysis   │  ← Determines marked bubbles
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Answer Extraction│  ← Generates answer string
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   JSON Output   │
└─────────────────┘
```

##  Deployment

### Deploy to Render (Free)

1. Push code to GitHub ✅ (Done!)
2. Go to [render.com](https://render.com)
3. New → Web Service → Connect repository
4. Render will auto-deploy!

### Deploy to Railway

```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

### Deploy to AWS/GCP

See complete deployment guide: [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md)

## 📁 Project Structure

```
omr-scanner-yolov8/
├── api_server.py           # REST API server
├── omr_processor.py        # Core OMR processing engine
├── test.py                 # Command-line tool
├── app.py                  # Web interface
├── batch_process.py        # Batch processing
├── frontend_example.html   # Integration example
├── requirements.txt        # Python dependencies
├── Procfile               # Cloud deployment config
├── data.yaml              # YOLOv8 configuration
├── .gitignore             # Git ignore rules
├── DEPLOYMENT_GUIDE.md    # Complete deployment guide
├── QUICK_DEPLOY.md        # Quick start guide
└── train/valid/test/      # Dataset structure (images not included)
```

## 🔧 Configuration

### Adjust Detection Parameters

Edit `omr_processor.py`:

```python
# Bubble size range
min_area = 20
max_area = 1000

# Fill detection sensitivity
fill_threshold = 0.25  # Lower = more sensitive

# Grouping thresholds
vertical_threshold = 8     # Pixels between rows
horizontal_threshold = 30  # Pixels between columns
```

## 📊 Model Information

- **Framework**: YOLOv8 (Ultralytics)
- **Classes**: 7 (m_area, mcqs, name, r_number, v_number, bubble_empty, bubble_filled)
- **Input Size**: 640x640
- **Training Dataset**: Custom OMR sheets dataset

## 🛠️ Requirements

- Python 3.9+
- OpenCV
- Ultralytics YOLOv8
- EasyOCR
- Flask & Flask-CORS
- NumPy
- Pillow

See [`requirements.txt`](requirements.txt) for complete list.

## 📚 Documentation

- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete deployment guide
- **[QUICK_DEPLOY.md](QUICK_DEPLOY.md)** - 5-minute quick start
- **[GITHUB_UPLOAD_GUIDE.md](GITHUB_UPLOAD_GUIDE.md)** - GitHub best practices

## 🔒 Security

- CORS enabled (configurable for specific domains)
- File type validation
- Size limits on uploads
- API key authentication ready (see deployment guide)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) for object detection
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) for text recognition
- [Flask](https://flask.palletsprojects.com/) for REST API

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check the documentation guides
- Review code comments in source files

## ⭐ Star History

If you find this project helpful, please consider giving it a star! ⭐

---

**Built with ❤️ using YOLOv8 and Computer Vision**

**Repository**: [github.com/bavi404/omr-scanner-yolov8](https://github.com/bavi404/omr-scanner-yolov8)

