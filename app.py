from flask import Flask, request, jsonify, render_template_string
import os
from werkzeug.utils import secure_filename
from omr_processor import OMRProcessor
import json

app = Flask(__name__)

# Configuration
MODEL_PATH = r"C:\Users\sanka\runs\detect\train3\weights\best.pt"
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create upload folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize OMR Processor
processor = OMRProcessor(MODEL_PATH)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>OMR Sheet Processor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            margin-bottom: 30px;
            background: #f8f9ff;
            transition: all 0.3s;
        }
        .upload-area:hover {
            background: #e8ebff;
            border-color: #764ba2;
        }
        input[type="file"] {
            display: none;
        }
        .upload-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .upload-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        .file-name {
            margin-top: 15px;
            color: #666;
            font-style: italic;
        }
        .submit-btn {
            background: #28a745;
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 25px;
            font-size: 18px;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s;
        }
        .submit-btn:hover {
            background: #218838;
            transform: translateY(-2px);
        }
        .submit-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .results {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9ff;
            border-radius: 10px;
            display: none;
        }
        .result-item {
            margin: 15px 0;
            padding: 15px;
            background: white;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .result-label {
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        .result-value {
            color: #333;
            font-size: 1.1em;
        }
        .answer-string {
            font-family: 'Courier New', monospace;
            background: #f0f0f0;
            padding: 10px;
            border-radius: 5px;
            word-break: break-all;
        }
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #dc3545;
            margin-top: 20px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 OMR Sheet Processor</h1>
        
        <form id="uploadForm" enctype="multipart/form-data">
            <div class="upload-area">
                <label for="fileInput" class="upload-btn">Choose OMR Image</label>
                <input type="file" id="fileInput" name="file" accept="image/*" required>
                <div class="file-name" id="fileName">No file chosen</div>
            </div>
            
            <button type="submit" class="submit-btn" id="submitBtn">
                Process OMR Sheet
            </button>
        </form>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Processing OMR sheet...</p>
        </div>
        
        <div class="error" id="error"></div>
        
        <div class="results" id="results">
            <h2>Results</h2>
            <div class="result-item">
                <div class="result-label">📝 Name</div>
                <div class="result-value" id="name">-</div>
            </div>
            <div class="result-item">
                <div class="result-label">🔢 Roll Number</div>
                <div class="result-value" id="rollNumber">-</div>
            </div>
            <div class="result-item">
                <div class="result-label">📋 Version</div>
                <div class="result-value" id="version">-</div>
            </div>
            <div class="result-item">
                <div class="result-label">✅ Total Questions Answered</div>
                <div class="result-value" id="totalQuestions">0</div>
            </div>
            <div class="result-item">
                <div class="result-label">📊 Answer String</div>
                <div class="result-value answer-string" id="answerString">-</div>
            </div>
        </div>
    </div>
    
    <script>
        const fileInput = document.getElementById('fileInput');
        const fileName = document.getElementById('fileName');
        const uploadForm = document.getElementById('uploadForm');
        const submitBtn = document.getElementById('submitBtn');
        const loading = document.getElementById('loading');
        const results = document.getElementById('results');
        const error = document.getElementById('error');
        
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                fileName.textContent = this.files[0].name;
            } else {
                fileName.textContent = 'No file chosen';
            }
        });
        
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (!fileInput.files[0]) {
                showError('Please select an image file');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            
            // Show loading
            submitBtn.disabled = true;
            loading.style.display = 'block';
            results.style.display = 'none';
            error.style.display = 'none';
            
            try {
                const response = await fetch('/process', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    displayResults(data);
                } else {
                    showError(data.error || 'Processing failed');
                }
            } catch (err) {
                showError('Network error: ' + err.message);
            } finally {
                submitBtn.disabled = false;
                loading.style.display = 'none';
            }
        });
        
        function displayResults(data) {
            document.getElementById('name').textContent = data.name || '-';
            document.getElementById('rollNumber').textContent = data.roll_number || '-';
            document.getElementById('version').textContent = data.version || '-';
            document.getElementById('totalQuestions').textContent = Object.keys(data.answers || {}).length;
            document.getElementById('answerString').textContent = data.answer_string || '-';
            
            results.style.display = 'block';
        }
        
        function showError(message) {
            error.textContent = '❌ ' + message;
            error.style.display = 'block';
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/process', methods=['POST'])
def process_omr():
    # Check if file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Use PNG, JPG, or JPEG'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Process OMR
        result = processor.process_omr(filepath, debug=False)
        
        # Clean up
        if os.path.exists(filepath):
            os.remove(filepath)
        
        if "error" in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'model_loaded': processor.model is not None})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 OMR Sheet Processor Server")
    print("="*60)
    print(f"📂 Model: {MODEL_PATH}")
    print(f"🌐 Server: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
