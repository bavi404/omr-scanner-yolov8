# 🚀 Deployment Guide - OMR Processing API

Complete guide to deploy your trained YOLOv8 model for website integration.

## Table of Contents
1. [Quick Start](#quick-start)
2. [Local Deployment](#local-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Website Integration](#website-integration)
5. [Security](#security)
6. [Scaling](#scaling)

---

## Quick Start

### 1. Install Additional Dependencies

```bash
pip install flask-cors gunicorn
```

### 2. Start the API Server

```bash
python api_server.py
```

The API will be available at: `http://localhost:5000`

---

## Local Deployment

### Option 1: Development Server (Testing)

```bash
python api_server.py
```

**Use for:** Testing locally before deployment

---

### Option 2: Production Server (Gunicorn)

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn (4 workers)
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

**Use for:** Local production deployment

---

## Cloud Deployment

### Option A: Deploy to Render (Easiest - Free Tier)

1. **Create `Procfile`:**
```bash
web: gunicorn api_server:app
```

2. **Push to GitHub**

3. **Connect to Render.com:**
   - Go to https://render.com
   - New > Web Service
   - Connect your GitHub repo
   - Set environment: Python 3
   - Deploy!

**Your API URL:** `https://your-app.onrender.com`

---

### Option B: Deploy to Railway

1. **Install Railway CLI:**
```bash
npm install -g @railway/cli
```

2. **Deploy:**
```bash
railway login
railway init
railway up
```

**Your API URL:** `https://your-app.railway.app`

---

### Option C: Deploy to AWS (Advanced)

#### Using AWS EC2:

1. **Launch EC2 Instance** (Ubuntu 22.04)

2. **SSH into instance:**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

3. **Install dependencies:**
```bash
sudo apt update
sudo apt install python3-pip nginx
pip3 install -r requirements.txt
pip3 install gunicorn flask-cors
```

4. **Copy your files:**
```bash
scp -r . ubuntu@your-ec2-ip:/home/ubuntu/omr-api/
```

5. **Run with supervisor:**
```bash
sudo apt install supervisor

# Create /etc/supervisor/conf.d/omr-api.conf
[program:omr-api]
directory=/home/ubuntu/omr-api
command=gunicorn -w 4 -b 127.0.0.1:5000 api_server:app
user=ubuntu
autostart=true
autorestart=true
```

6. **Setup Nginx:**
```nginx
# /etc/nginx/sites-available/omr-api
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

7. **Enable and restart:**
```bash
sudo ln -s /etc/nginx/sites-available/omr-api /etc/nginx/sites-enabled/
sudo systemctl restart nginx
sudo supervisorctl reread
sudo supervisorctl update
```

**Your API URL:** `http://your-domain.com`

---

### Option D: Deploy to Google Cloud Run (Serverless)

1. **Create `Dockerfile`:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn flask-cors

COPY . .

CMD exec gunicorn --bind :$PORT api_server:app
```

2. **Deploy:**
```bash
gcloud run deploy omr-api --source . --platform managed --region us-central1 --allow-unauthenticated
```

**Your API URL:** `https://omr-api-xxxxx.run.app`

---

## Website Integration

### Frontend Example (JavaScript/HTML)

#### Example 1: Simple Form Upload

```html
<!DOCTYPE html>
<html>
<head>
    <title>OMR Scanner</title>
</head>
<body>
    <h1>OMR Sheet Scanner</h1>
    
    <input type="file" id="fileInput" accept="image/*">
    <button onclick="processOMR()">Process OMR</button>
    
    <div id="results"></div>

    <script>
        async function processOMR() {
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('Please select a file');
                return;
            }
            
            // Create form data
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                // Call API
                const response = await fetch('http://localhost:5000/api/process', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                // Display results
                document.getElementById('results').innerHTML = `
                    <h2>Results</h2>
                    <p><strong>Name:</strong> ${data.name}</p>
                    <p><strong>Roll Number:</strong> ${data.roll_number}</p>
                    <p><strong>Version:</strong> ${data.version}</p>
                    <p><strong>Questions Detected:</strong> ${Object.keys(data.answers).length}</p>
                    <p><strong>Answer String:</strong> ${data.answer_string}</p>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                `;
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }
    </script>
</body>
</html>
```

---

#### Example 2: React Component

```jsx
import React, { useState } from 'react';

function OMRScanner() {
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    
    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;
        
        setLoading(true);
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('http://your-api-url.com/api/process', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            setResults(data);
        } catch (error) {
            console.error('Error:', error);
            alert('Processing failed');
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <div>
            <h1>OMR Sheet Scanner</h1>
            <input 
                type="file" 
                onChange={handleFileUpload} 
                accept="image/*"
                disabled={loading}
            />
            
            {loading && <p>Processing...</p>}
            
            {results && (
                <div>
                    <h2>Results</h2>
                    <p><strong>Name:</strong> {results.name}</p>
                    <p><strong>Roll Number:</strong> {results.roll_number}</p>
                    <p><strong>Answer String:</strong> {results.answer_string}</p>
                    <h3>Answers:</h3>
                    <ul>
                        {Object.entries(results.answers).map(([q, ans]) => (
                            <li key={q}>{q}: {ans}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

export default OMRScanner;
```

---

#### Example 3: Base64 Upload (Mobile Apps)

```javascript
// Convert image to base64
function imageToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

async function processOMRBase64(file) {
    const base64Image = await imageToBase64(file);
    
    const response = await fetch('http://localhost:5000/api/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            image: base64Image
        })
    });
    
    return await response.json();
}
```

---

#### Example 4: cURL (Testing)

```bash
# Upload file
curl -X POST \
  -F "file=@test_image.jpg" \
  http://localhost:5000/api/process

# Base64 upload
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"image":"data:image/jpeg;base64,/9j/4AAQ..."}' \
  http://localhost:5000/api/process

# Health check
curl http://localhost:5000/api/health

# Batch processing
curl -X POST \
  -F "files[]=@omr1.jpg" \
  -F "files[]=@omr2.jpg" \
  http://localhost:5000/api/batch
```

---

## Security

### 1. Add API Key Authentication

Add to `api_server.py`:

```python
from functools import wraps

API_KEY = "your-secret-api-key-here"

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != API_KEY:
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Use on endpoints
@app.route('/api/process', methods=['POST'])
@require_api_key
def process_omr():
    # ... your code
```

Frontend usage:
```javascript
fetch('http://your-api/api/process', {
    method: 'POST',
    headers: {
        'X-API-Key': 'your-secret-api-key-here'
    },
    body: formData
});
```

---

### 2. Rate Limiting

```bash
pip install flask-limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/process', methods=['POST'])
@limiter.limit("10 per minute")
def process_omr():
    # ... your code
```

---

### 3. HTTPS (SSL)

For production, always use HTTPS:

```bash
# With Let's Encrypt (free SSL)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

### 4. Environment Variables

Never hardcode paths. Use environment variables:

```python
import os

MODEL_PATH = os.getenv('MODEL_PATH', 'default/path/to/model.pt')
API_KEY = os.getenv('API_KEY', 'default-key')
```

---

## Scaling

### 1. Add Redis Caching

```bash
pip install redis
```

```python
import redis
import hashlib

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@app.route('/api/process', methods=['POST'])
def process_omr():
    # Create hash of image
    file_hash = hashlib.md5(file.read()).hexdigest()
    file.seek(0)
    
    # Check cache
    cached = redis_client.get(file_hash)
    if cached:
        return jsonify(json.loads(cached)), 200
    
    # Process
    result = processor.process_omr(filepath)
    
    # Cache for 1 hour
    redis_client.setex(file_hash, 3600, json.dumps(result))
    
    return jsonify(result), 200
```

---

### 2. Load Balancing (Nginx)

```nginx
upstream omr_api {
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
    server 127.0.0.1:5004;
}

server {
    listen 80;
    location / {
        proxy_pass http://omr_api;
    }
}
```

---

### 3. Docker Deployment

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./models:/app/models
    environment:
      - MODEL_PATH=/app/models/best.pt
    deploy:
      replicas: 4
```

---

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Check if API is running |
| `/api/process` | POST | Process single OMR |
| `/api/batch` | POST | Process multiple OMRs |
| `/api/validate` | POST | Validate answers |
| `/api/model-info` | GET | Get model information |

---

## Testing Your Deployment

```bash
# Health check
curl http://your-api-url/api/health

# Process OMR
curl -X POST -F "file=@test.jpg" http://your-api-url/api/process

# Check response time
curl -w "@curl-format.txt" -o /dev/null -s http://your-api-url/api/health
```

---

## Troubleshooting

### CORS Issues
- Make sure `flask-cors` is installed
- Check the `origins` setting in `api_server.py`
- Add your friend's website domain to allowed origins

### Model Not Loading
- Verify `MODEL_PATH` is correct
- Check file permissions
- Ensure model file exists

### Slow Processing
- Use GPU (install CUDA-enabled PyTorch)
- Implement caching
- Use load balancing

---

## 🎯 Recommended Deployment Path

**For Your Friend's Website:**

1. **Start Local:** Test with `python api_server.py`
2. **Deploy to Render:** Free, easy, gets you HTTPS URL
3. **Add to Website:** Use JavaScript fetch examples
4. **Add Security:** Implement API key
5. **Scale if Needed:** Move to AWS/GCP with load balancing

**Estimated Cost:**
- Render Free Tier: $0/month
- AWS EC2 t2.micro: ~$10/month
- Google Cloud Run: Pay per use (~$5-20/month)

---

## Support

Your API is production-ready! Any questions, check the code comments in `api_server.py`.

**Happy Deploying! 🚀**

