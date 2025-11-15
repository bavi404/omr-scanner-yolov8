"""
Production API Server for OMR Sheet Processor
Designed for deployment on Render.com
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename
from omr_processor import OMRProcessor
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Configuration
MODEL_PATH = os.environ.get('MODEL_PATH', 'best.pt')
UPLOAD_FOLDER = 'temp_uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize OMR Processor (lazy loading)
processor = None

def get_processor():
    """Lazy load the processor to avoid loading on import"""
    global processor
    if processor is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
        processor = OMRProcessor(MODEL_PATH)
    return processor

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def decode_base64_image(base64_string):
    """Decode base64 image string to OpenCV format"""
    # Remove header if present
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    
    # Decode base64
    img_data = base64.b64decode(base64_string)
    
    # Convert to PIL Image then to OpenCV
    pil_image = Image.open(BytesIO(img_data))
    opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    return opencv_image

@app.route('/')
def home():
    """API documentation endpoint"""
    return jsonify({
        "service": "OMR Sheet Processor API",
        "version": "1.0",
        "status": "running",
        "endpoints": {
            "/api/process": {
                "method": "POST",
                "description": "Process OMR sheet image",
                "content_types": ["multipart/form-data", "application/json"],
                "parameters": {
                    "file": "Image file (multipart/form-data)",
                    "image": "Base64 encoded image (JSON)",
                    "format": "Output format: 'full' or 'simple' (default: 'simple')"
                }
            },
            "/api/health": {
                "method": "GET",
                "description": "Health check endpoint"
            }
        },
        "documentation": "https://github.com/bavi404/omr-sheet-processor"
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        proc = get_processor()
        model_loaded = proc.model is not None
    except:
        model_loaded = False
    
    return jsonify({
        "status": "healthy" if model_loaded else "initializing",
        "model_loaded": model_loaded,
        "service": "OMR Processor API"
    })

@app.route('/api/process', methods=['POST'])
def process_omr():
    """
    Process OMR sheet and return extracted data
    
    Accepts either:
    1. Multipart form data with 'file' field
    2. JSON with base64 encoded 'image' field
    """
    try:
        # Get processor instance
        proc = get_processor()
        
        # Get output format
        output_format = request.form.get('format', 'simple') if request.form else request.json.get('format', 'simple')
        
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'error': 'Invalid file type. Use PNG, JPG, or JPEG'}), 400
            
            # Save temporarily
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Process OMR
            result = proc.process_omr(filepath, debug=False)
            
            # Clean up
            if os.path.exists(filepath):
                os.remove(filepath)
        
        # Handle base64 image
        elif request.is_json and 'image' in request.json:
            base64_image = request.json['image']
            
            # Decode base64 to image
            image = decode_base64_image(base64_image)
            
            # Save temporarily
            temp_path = os.path.join(UPLOAD_FOLDER, 'temp_image.jpg')
            cv2.imwrite(temp_path, image)
            
            # Process OMR
            result = proc.process_omr(temp_path, debug=False)
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        else:
            return jsonify({'error': 'No image provided. Send file or base64 encoded image'}), 400
        
        # Check for processing errors
        if "error" in result:
            return jsonify({'error': result['error']}), 500
        
        # Format response based on requested format
        if output_format == 'full':
            response = result
        else:  # simple format
            response = {
                'success': True,
                'name': result.get('name', ''),
                'roll_number': result.get('roll_number', ''),
                'version': result.get('version', ''),
                'answer_string': result.get('answer_string', ''),
                'total_questions': len(result.get('answers', {}))
            }
        
        return jsonify(response), 200
    
    except FileNotFoundError as e:
        return jsonify({'error': f'Model file not found: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/api/batch', methods=['POST'])
def batch_process():
    """
    Process multiple OMR sheets at once
    Accepts JSON array of base64 encoded images
    """
    try:
        if not request.is_json or 'images' not in request.json:
            return jsonify({'error': 'Send JSON with "images" array of base64 strings'}), 400
        
        images = request.json['images']
        
        if not isinstance(images, list):
            return jsonify({'error': '"images" must be an array'}), 400
        
        if len(images) > 10:
            return jsonify({'error': 'Maximum 10 images per batch'}), 400
        
        proc = get_processor()
        results = []
        
        for idx, base64_image in enumerate(images):
            try:
                # Decode and save temporarily
                image = decode_base64_image(base64_image)
                temp_path = os.path.join(UPLOAD_FOLDER, f'batch_{idx}.jpg')
                cv2.imwrite(temp_path, image)
                
                # Process
                result = proc.process_omr(temp_path, debug=False)
                
                # Clean up
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                # Simplified result
                results.append({
                    'index': idx,
                    'success': True,
                    'name': result.get('name', ''),
                    'roll_number': result.get('roll_number', ''),
                    'answer_string': result.get('answer_string', ''),
                    'total_questions': len(result.get('answers', {}))
                })
            
            except Exception as e:
                results.append({
                    'index': idx,
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'processed': len(results),
            'results': results
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Batch processing failed: {str(e)}'}), 500

# Error handlers
@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    
    print("\n" + "="*60)
    print("🚀 OMR Sheet Processor API Server")
    print("="*60)
    print(f"📂 Model: {MODEL_PATH}")
    print(f"🌐 Port: {port}")
    print(f"📡 CORS: Enabled")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)

