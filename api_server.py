"""
Production-Ready REST API for OMR Processing
Can be integrated into any website
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import base64
from werkzeug.utils import secure_filename
from omr_processor import OMRProcessor
import json
import io
from PIL import Image
import cv2
import numpy as np

app = Flask(__name__)

# Enable CORS for cross-origin requests (allows website integration)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # Change to your friend's website domain in production
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuration
MODEL_PATH = r"C:\Users\sanka\runs\detect\train3\weights\best.pt"
UPLOAD_FOLDER = 'api_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Create upload folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize OMR Processor (loaded once at startup)
print("Loading OMR model...")
processor = OMRProcessor(MODEL_PATH)
print("Model loaded successfully!")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def decode_base64_image(base64_string):
    """Decode base64 image string to numpy array."""
    try:
        # Remove data URL prefix if present
        if 'base64,' in base64_string:
            base64_string = base64_string.split('base64,')[1]
        
        img_data = base64.b64decode(base64_string)
        img = Image.open(io.BytesIO(img_data))
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    except Exception as e:
        return None

# ============================================================
# API ENDPOINTS
# ============================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint - verify API is running."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': processor.model is not None,
        'service': 'OMR Processing API',
        'version': '1.0.0'
    }), 200


@app.route('/api/process', methods=['POST'])
def process_omr():
    """
    Main endpoint to process OMR sheets.
    
    Accepts:
    - multipart/form-data with 'file' field (image file)
    - application/json with 'image' field (base64 encoded)
    
    Returns:
    - JSON with extracted data
    """
    
    # Check if request has file or base64 image
    if 'file' in request.files:
        # File upload
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file type',
                'allowed_types': list(ALLOWED_EXTENSIONS)
            }), 400
        
        # Save temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
    elif request.is_json and 'image' in request.json:
        # Base64 encoded image
        base64_image = request.json['image']
        image_array = decode_base64_image(base64_image)
        
        if image_array is None:
            return jsonify({'error': 'Invalid base64 image'}), 400
        
        # Save temporarily
        filename = 'temp_image.jpg'
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        cv2.imwrite(filepath, image_array)
        
    else:
        return jsonify({
            'error': 'No image provided',
            'help': 'Send image as multipart/form-data with "file" field or as JSON with "image" (base64) field'
        }), 400
    
    try:
        # Process OMR
        result = processor.process_omr(filepath, debug=False)
        
        # Clean up
        if os.path.exists(filepath):
            os.remove(filepath)
        
        if "error" in result:
            return jsonify({'error': result['error']}), 500
        
        # Add metadata
        result['metadata'] = {
            'filename': filename,
            'questions_detected': len(result.get('answers', {})),
            'processing_status': 'success'
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            'error': str(e),
            'processing_status': 'failed'
        }), 500


@app.route('/api/batch', methods=['POST'])
def batch_process():
    """
    Process multiple OMR sheets at once.
    
    Accepts:
    - multipart/form-data with multiple 'files[]' fields
    
    Returns:
    - JSON array with results for each image
    """
    
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files[]')
    
    if not files or len(files) == 0:
        return jsonify({'error': 'No files selected'}), 400
    
    results = []
    
    for file in files:
        if file.filename == '' or not allowed_file(file.filename):
            results.append({
                'filename': file.filename,
                'status': 'error',
                'error': 'Invalid file'
            })
            continue
        
        try:
            # Save and process
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            result = processor.process_omr(filepath, debug=False)
            result['filename'] = filename
            result['status'] = 'success'
            
            results.append(result)
            
            # Clean up
            if os.path.exists(filepath):
                os.remove(filepath)
                
        except Exception as e:
            results.append({
                'filename': file.filename,
                'status': 'error',
                'error': str(e)
            })
    
    return jsonify({
        'total': len(files),
        'processed': len([r for r in results if r.get('status') == 'success']),
        'failed': len([r for r in results if r.get('status') == 'error']),
        'results': results
    }), 200


@app.route('/api/validate', methods=['POST'])
def validate_answers():
    """
    Validate detected answers against answer key.
    
    Accepts:
    - JSON with 'detected_answers' and 'answer_key' fields
    
    Returns:
    - Score and detailed comparison
    """
    
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    data = request.json
    
    if 'detected_answers' not in data or 'answer_key' not in data:
        return jsonify({
            'error': 'Missing required fields',
            'required': ['detected_answers', 'answer_key']
        }), 400
    
    detected = data['detected_answers']
    answer_key = data['answer_key']
    
    # Compare answers
    comparison = []
    correct = 0
    total = 0
    
    for q_num in answer_key:
        detected_ans = detected.get(q_num)
        correct_ans = answer_key[q_num]
        
        is_correct = detected_ans == correct_ans
        if is_correct:
            correct += 1
        
        comparison.append({
            'question': q_num,
            'detected': detected_ans,
            'correct': correct_ans,
            'is_correct': is_correct
        })
        
        total += 1
    
    score_percentage = (correct / total * 100) if total > 0 else 0
    
    return jsonify({
        'score': correct,
        'total': total,
        'percentage': round(score_percentage, 2),
        'grade': get_grade(score_percentage),
        'comparison': comparison
    }), 200


def get_grade(percentage):
    """Convert percentage to letter grade."""
    if percentage >= 90:
        return 'A+'
    elif percentage >= 80:
        return 'A'
    elif percentage >= 70:
        return 'B'
    elif percentage >= 60:
        return 'C'
    elif percentage >= 50:
        return 'D'
    else:
        return 'F'


@app.route('/api/model-info', methods=['GET'])
def model_info():
    """Get information about the loaded model."""
    return jsonify({
        'model_type': 'YOLOv8',
        'model_path': MODEL_PATH,
        'classes': processor.model.names,
        'num_classes': len(processor.model.names),
        'input_size': '640x640',
        'supported_formats': list(ALLOWED_EXTENSIONS)
    }), 200


@app.route('/', methods=['GET'])
def index():
    """API documentation homepage."""
    return jsonify({
        'service': 'OMR Processing API',
        'version': '1.0.0',
        'endpoints': {
            '/api/health': 'GET - Health check',
            '/api/process': 'POST - Process single OMR sheet',
            '/api/batch': 'POST - Process multiple OMR sheets',
            '/api/validate': 'POST - Validate answers against answer key',
            '/api/model-info': 'GET - Get model information'
        },
        'documentation': '/api/docs',
        'usage': {
            'example_curl': 'curl -X POST -F "file=@omr.jpg" http://localhost:5000/api/process',
            'example_javascript': 'fetch("http://localhost:5000/api/process", {method: "POST", body: formData})'
        }
    }), 200


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': ['/api/process', '/api/batch', '/api/validate', '/api/health']
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': str(error)
    }), 500


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 OMR PROCESSING API SERVER")
    print("="*60)
    print(f"📂 Model: {MODEL_PATH}")
    print(f"🌐 API URL: http://localhost:5000")
    print(f"📡 CORS: Enabled (allows website integration)")
    print("\n📚 Available Endpoints:")
    print("  • POST /api/process     - Process single OMR")
    print("  • POST /api/batch       - Process multiple OMRs")
    print("  • POST /api/validate    - Validate answers")
    print("  • GET  /api/health      - Health check")
    print("  • GET  /api/model-info  - Model information")
    print("="*60 + "\n")
    
    # Run server
    # For development
    # app.run(debug=True, host='0.0.0.0', port=5000)
    
    # For production (use with gunicorn)
    app.run(host='0.0.0.0', port=5000)

