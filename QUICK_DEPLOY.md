# 🚀 Quick Deploy Guide

## Step 1: Install Dependencies

```bash
pip install flask-cors gunicorn
```

## Step 2: Start API Server Locally

```bash
python api_server.py
```

✅ Your API is now running at: **http://localhost:5000**

## Step 3: Test the API

Open `frontend_example.html` in your browser or use curl:

```bash
curl -X POST -F "file=@test/images/test_img_20.jpg" http://localhost:5000/api/process
```

## Step 4: Deploy to Cloud (Free)

### Option A: Render.com (Easiest)

1. Create account at https://render.com
2. Push code to GitHub
3. New > Web Service > Connect GitHub repo
4. Render will auto-detect Python and deploy!
5. Your API URL: `https://your-app.onrender.com`

### Option B: Railway.app

```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

Your API URL: `https://your-app.railway.app`

## Step 5: Integrate with Website

Use this code in your friend's website:

```javascript
async function processOMR(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('https://your-api-url.com/api/process', {
        method: 'POST',
        body: formData
    });
    
    return await response.json();
}
```

## API Endpoints

- `POST /api/process` - Process single OMR
- `POST /api/batch` - Process multiple OMRs
- `GET /api/health` - Health check
- `GET /api/model-info` - Model details

## Example Response

```json
{
    "name": "John Doe",
    "roll_number": "12345",
    "version": "A",
    "answers": {
        "Q1": "A",
        "Q2": "B",
        "Q3": "C"
    },
    "answer_string": "ABC..."
}
```

## That's It! 🎉

Your YOLOv8 OMR model is now accessible via REST API!

For detailed deployment options, see **DEPLOYMENT_GUIDE.md**

