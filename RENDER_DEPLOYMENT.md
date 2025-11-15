# 🚀 Deploying to Render.com

This guide will help you deploy the OMR Sheet Processor as a REST API on Render.com, allowing you to use it from any other project.

## 📋 Prerequisites

1. **GitHub Account** - Your code is already on GitHub
2. **Render Account** - Sign up at [render.com](https://render.com) (free tier available)
3. **Model File** - Your trained `best.pt` model hosted somewhere accessible

## 🎯 Step-by-Step Deployment

### Step 1: Host Your Model File

Your model file (`best.pt`, ~22MB) needs to be accessible via URL. Options:

#### Option A: GitHub Releases (Recommended)
1. Go to your repo: https://github.com/bavi404/omr-sheet-processor
2. Click "Releases" → "Create a new release"
3. Tag: `v1.0.0`, Title: `Initial Release`
4. Upload your `best.pt` file as an asset
5. Publish release
6. Copy the download URL (right-click on the file → Copy link)

#### Option B: Google Drive
1. Upload `best.pt` to Google Drive
2. Right-click → Get link → Change to "Anyone with link can view"
3. Copy the file ID from URL: `https://drive.google.com/file/d/FILE_ID/view`
4. Use this URL format: `https://drive.google.com/uc?export=download&id=FILE_ID`

#### Option C: Dropbox
1. Upload `best.pt` to Dropbox
2. Get sharing link
3. Change `www.dropbox.com` to `dl.dropboxusercontent.com`
4. Change `?dl=0` to `?dl=1`

### Step 2: Deploy to Render

1. **Go to Render Dashboard**
   - Visit [dashboard.render.com](https://dashboard.render.com)
   - Click "New +" → "Web Service"

2. **Connect GitHub Repository**
   - Connect your GitHub account if not already connected
   - Select: `bavi404/omr-sheet-processor`
   - Click "Connect"

3. **Configure Service**
   ```
   Name:              omr-processor-api
   Environment:       Python 3
   Region:            Choose closest to you
   Branch:            main
   Build Command:     pip install -r requirements.txt && python download_model.py
   Start Command:     gunicorn api_server:app
   ```

4. **Set Environment Variables**
   - Click "Advanced" → "Add Environment Variable"
   
   Add these variables:
   ```
   MODEL_DOWNLOAD_URL = [Your model URL from Step 1]
   MODEL_PATH = best.pt
   PORT = 10000
   PYTHON_VERSION = 3.10.0
   ```

5. **Choose Plan**
   - Free tier is sufficient for testing
   - Upgrade to paid for production use

6. **Deploy!**
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - Your API will be live at: `https://your-service-name.onrender.com`

### Step 3: Test Your API

Once deployed, test with:

```bash
curl https://your-service-name.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "service": "OMR Processor API"
}
```

## 🔌 Using the API

### API Endpoints

#### 1. Health Check
```http
GET /api/health
```

#### 2. Process Single Image
```http
POST /api/process
Content-Type: multipart/form-data

file: [OMR image file]
format: simple|full (optional)
```

#### 3. Process with Base64
```http
POST /api/process
Content-Type: application/json

{
  "image": "base64_encoded_image_string",
  "format": "simple"
}
```

#### 4. Batch Processing
```http
POST /api/batch
Content-Type: application/json

{
  "images": ["base64_1", "base64_2", ...]
}
```

### Example: JavaScript/Node.js

```javascript
// Using fetch API
async function processOMR(imageFile) {
  const formData = new FormData();
  formData.append('file', imageFile);
  formData.append('format', 'simple');
  
  const response = await fetch('https://your-service.onrender.com/api/process', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  console.log('Answer String:', result.answer_string);
  console.log('Name:', result.name);
  console.log('Roll Number:', result.roll_number);
  
  return result;
}
```

### Example: Python

```python
import requests

# Process image file
def process_omr(image_path):
    url = 'https://your-service.onrender.com/api/process'
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {'format': 'simple'}
        response = requests.post(url, files=files, data=data)
    
    result = response.json()
    print(f"Answer String: {result['answer_string']}")
    print(f"Name: {result['name']}")
    
    return result

# Process base64 image
def process_base64(base64_string):
    url = 'https://your-service.onrender.com/api/process'
    
    payload = {
        'image': base64_string,
        'format': 'simple'
    }
    
    response = requests.post(url, json=payload)
    return response.json()
```

### Example: React

```jsx
import React, { useState } from 'react';

function OMRUpload() {
  const [result, setResult] = useState(null);
  
  const handleUpload = async (event) => {
    const file = event.target.files[0];
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('https://your-service.onrender.com/api/process', {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    setResult(data);
  };
  
  return (
    <div>
      <input type="file" onChange={handleUpload} accept="image/*" />
      {result && (
        <div>
          <p>Name: {result.name}</p>
          <p>Roll Number: {result.roll_number}</p>
          <p>Answer String: {result.answer_string}</p>
        </div>
      )}
    </div>
  );
}
```

### Example: cURL

```bash
# Upload file
curl -X POST \
  -F "file=@omr_sheet.jpg" \
  -F "format=simple" \
  https://your-service.onrender.com/api/process

# Base64 image
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"image":"base64_string_here","format":"simple"}' \
  https://your-service.onrender.com/api/process
```

## 📊 Response Format

### Simple Format (default)
```json
{
  "success": true,
  "name": "John Doe",
  "roll_number": "123456",
  "version": "A",
  "answer_string": "ABCDABCDABCD",
  "total_questions": 50
}
```

### Full Format
```json
{
  "name": "John Doe",
  "roll_number": "123456",
  "version": "A",
  "answers": {
    "Q1": "A",
    "Q2": "B",
    "Q3": "C",
    ...
  },
  "answer_string": "ABCDABCDABCD"
}
```

## 🔧 Troubleshooting

### Build Fails
- Check that `MODEL_DOWNLOAD_URL` is set correctly
- Ensure model URL is a direct download link
- Check Render logs for specific errors

### Model Not Loading
- Verify model file was downloaded (check logs)
- Ensure model file is `best.pt` in root directory
- Check file size matches your original model

### Slow Response
- Free tier "spins down" after inactivity
- First request after idle takes ~30 seconds
- Upgrade to paid tier for always-on service

### Out of Memory
- Free tier has 512MB RAM
- Model + dependencies might exceed this
- Upgrade to Starter plan ($7/month) with 2GB RAM

## 💡 Tips

1. **Use Health Check**: Monitor `/api/health` to keep service alive
2. **Batch Processing**: Process multiple images in one request for efficiency
3. **Compression**: Compress images before sending to reduce latency
4. **Error Handling**: Always check response status and handle errors
5. **Rate Limiting**: Be mindful of API usage on free tier

## 🚀 Production Checklist

- [ ] Model file successfully hosted and downloadable
- [ ] Environment variables set in Render
- [ ] Service deployed and running
- [ ] Health check endpoint returning healthy
- [ ] Test with sample image successful
- [ ] Error handling tested
- [ ] CORS enabled (already configured)
- [ ] Consider upgrading to paid tier for production

## 📞 Support

- **GitHub Issues**: https://github.com/bavi404/omr-sheet-processor/issues
- **Render Docs**: https://render.com/docs
- **API Status**: Check `/api/health` endpoint

---

**Your OMR Processor is now available as a REST API!** 🎉

Access it from any programming language, mobile app, web app, or service.

