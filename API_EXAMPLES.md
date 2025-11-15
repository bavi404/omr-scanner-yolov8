# 🔌 API Integration Examples

Examples of using the OMR Processor API in different projects and languages.

## Base URL
```
https://your-service-name.onrender.com
```

Replace `your-service-name` with your actual Render service name.

---

## JavaScript / TypeScript

### Vanilla JavaScript

```javascript
// Upload file
async function processOMRFile(fileInput) {
  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await fetch('https://your-service.onrender.com/api/process', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) throw new Error('Processing failed');
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

// Usage
document.getElementById('omrFile').addEventListener('change', async (e) => {
  const result = await processOMRFile(e.target);
  console.log('Answer String:', result.answer_string);
  console.log('Name:', result.name);
  console.log('Total Questions:', result.total_questions);
});
```

### React Hook

```jsx
import { useState } from 'react';

function useOMRProcessor(apiUrl) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  
  const processImage = async (file) => {
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch(`${apiUrl}/api/process`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) throw new Error('Processing failed');
      
      const data = await response.json();
      setResult(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };
  
  return { processImage, loading, error, result };
}

// Usage in component
function OMRUpload() {
  const { processImage, loading, result } = useOMRProcessor(
    'https://your-service.onrender.com'
  );
  
  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (file) await processImage(file);
  };
  
  return (
    <div>
      <input type="file" onChange={handleFileChange} accept="image/*" />
      {loading && <p>Processing...</p>}
      {result && (
        <div>
          <h3>Results:</h3>
          <p>Name: {result.name}</p>
          <p>Roll Number: {result.roll_number}</p>
          <p>Answer String: {result.answer_string}</p>
        </div>
      )}
    </div>
  );
}
```

### Next.js API Route

```javascript
// pages/api/process-omr.js
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  try {
    const formData = new FormData();
    formData.append('file', req.body.file);
    
    const response = await fetch('https://your-service.onrender.com/api/process', {
      method: 'POST',
      body: formData
    });
    
    const result = await response.json();
    res.status(200).json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
```

---

## Python

### Simple Request

```python
import requests

def process_omr(image_path):
    """Process OMR sheet and return results"""
    url = 'https://your-service.onrender.com/api/process'
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.json()}")

# Usage
result = process_omr('omr_sheet.jpg')
print(f"Answer String: {result['answer_string']}")
print(f"Name: {result['name']}")
```

### With Base64 Encoding

```python
import requests
import base64

def process_omr_base64(image_path):
    """Process OMR using base64 encoding"""
    url = 'https://your-service.onrender.com/api/process'
    
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Send request
    payload = {'image': image_data, 'format': 'simple'}
    response = requests.post(url, json=payload)
    
    return response.json()
```

### Batch Processing

```python
import requests
import base64
from pathlib import Path

def batch_process_omr(image_paths):
    """Process multiple OMR sheets at once"""
    url = 'https://your-service.onrender.com/api/batch'
    
    # Encode all images
    images = []
    for path in image_paths:
        with open(path, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
            images.append(encoded)
    
    # Send batch request
    payload = {'images': images}
    response = requests.post(url, json=payload)
    
    return response.json()

# Usage
results = batch_process_omr(['sheet1.jpg', 'sheet2.jpg', 'sheet3.jpg'])
for r in results['results']:
    print(f"Sheet {r['index']}: {r['answer_string']}")
```

### Django Integration

```python
# views.py
from django.http import JsonResponse
from django.views import View
import requests

class ProcessOMRView(View):
    API_URL = 'https://your-service.onrender.com/api/process'
    
    def post(self, request):
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        file = request.FILES['file']
        
        try:
            files = {'file': file}
            response = requests.post(self.API_URL, files=files)
            result = response.json()
            
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
```

### Flask Integration

```python
# app.py
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
OMR_API_URL = 'https://your-service.onrender.com/api/process'

@app.route('/grade-exam', methods=['POST'])
def grade_exam():
    if 'omr_sheet' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['omr_sheet']
    
    # Forward to OMR API
    files = {'file': file}
    response = requests.post(OMR_API_URL, files=files)
    
    result = response.json()
    
    # Compare with answer key (your logic here)
    answer_key = "ABCDABCD..."  # Your correct answers
    student_answers = result['answer_string']
    
    score = sum(1 for a, b in zip(answer_key, student_answers) if a == b)
    
    return jsonify({
        'name': result['name'],
        'roll_number': result['roll_number'],
        'score': score,
        'total': len(answer_key),
        'percentage': (score / len(answer_key)) * 100
    })
```

---

## PHP

```php
<?php
function processOMR($imagePath) {
    $url = 'https://your-service.onrender.com/api/process';
    
    $curl = curl_init();
    
    $file = new CURLFile($imagePath);
    $data = array('file' => $file);
    
    curl_setopt_array($curl, array(
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => $data
    ));
    
    $response = curl_exec($curl);
    curl_close($curl);
    
    return json_decode($response, true);
}

// Usage
$result = processOMR('omr_sheet.jpg');
echo "Answer String: " . $result['answer_string'];
echo "Name: " . $result['name'];
?>
```

---

## Mobile Apps

### React Native

```javascript
import { launchImageLibrary } from 'react-native-image-picker';

async function processOMRSheet() {
  // Pick image
  const result = await launchImageLibrary({
    mediaType: 'photo',
    quality: 1
  });
  
  if (result.didCancel) return;
  
  // Prepare form data
  const formData = new FormData();
  formData.append('file', {
    uri: result.assets[0].uri,
    type: result.assets[0].type,
    name: 'omr_sheet.jpg'
  });
  
  // Send to API
  try {
    const response = await fetch('https://your-service.onrender.com/api/process', {
      method: 'POST',
      body: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    const data = await response.json();
    console.log('Results:', data);
    return data;
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### Flutter

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<Map<String, dynamic>> processOMR(String imagePath) async {
  var uri = Uri.parse('https://your-service.onrender.com/api/process');
  
  var request = http.MultipartRequest('POST', uri);
  request.files.add(await http.MultipartFile.fromPath('file', imagePath));
  
  var response = await request.send();
  var responseData = await response.stream.toBytes();
  var responseString = String.fromCharCodes(responseData);
  
  return json.decode(responseString);
}

// Usage
void main() async {
  var result = await processOMR('/path/to/omr_sheet.jpg');
  print('Answer String: ${result['answer_string']}');
  print('Name: ${result['name']}');
}
```

---

## Error Handling

```javascript
async function processOMRWithErrorHandling(file) {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('https://your-service.onrender.com/api/process', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Processing failed');
    }
    
    return await response.json();
    
  } catch (error) {
    if (error.message.includes('Network')) {
      console.error('Network error - API might be down');
    } else if (error.message.includes('timeout')) {
      console.error('Request timeout - try again');
    } else {
      console.error('Processing error:', error.message);
    }
    throw error;
  }
}
```

---

## Testing the API

### cURL Examples

```bash
# Health check
curl https://your-service.onrender.com/api/health

# Process image
curl -X POST \
  -F "file=@omr_sheet.jpg" \
  https://your-service.onrender.com/api/process

# Get full response
curl -X POST \
  -F "file=@omr_sheet.jpg" \
  -F "format=full" \
  https://your-service.onrender.com/api/process
```

### Postman Collection

Import this JSON into Postman:

```json
{
  "info": {
    "name": "OMR Processor API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/health"
      }
    },
    {
      "name": "Process OMR Sheet",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/api/process",
        "body": {
          "mode": "formdata",
          "formdata": [
            {
              "key": "file",
              "type": "file",
              "src": "/path/to/omr_sheet.jpg"
            }
          ]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "https://your-service.onrender.com"
    }
  ]
}
```

---

## Rate Limiting Best Practices

```javascript
class OMRAPIClient {
  constructor(baseURL, maxRetries = 3) {
    this.baseURL = baseURL;
    this.maxRetries = maxRetries;
  }
  
  async processWithRetry(file, attempt = 1) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch(`${this.baseURL}/api/process`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) throw new Error('Processing failed');
      
      return await response.json();
      
    } catch (error) {
      if (attempt < this.maxRetries) {
        // Exponential backoff
        const delay = Math.pow(2, attempt) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
        return this.processWithRetry(file, attempt + 1);
      }
      throw error;
    }
  }
}

// Usage
const client = new OMRAPIClient('https://your-service.onrender.com');
const result = await client.processWithRetry(imageFile);
```

---

## 🎯 Quick Start Template

Copy-paste and replace `YOUR_SERVICE_URL`:

```javascript
const OMR_API = 'YOUR_SERVICE_URL';

async function gradeExam(imageFile) {
  const formData = new FormData();
  formData.append('file', imageFile);
  
  const response = await fetch(`${OMR_API}/api/process`, {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  
  // Your answer key
  const answerKey = "ABCDABCDABCD...";
  
  // Calculate score
  let score = 0;
  for (let i = 0; i < answerKey.length; i++) {
    if (result.answer_string[i] === answerKey[i]) score++;
  }
  
  return {
    name: result.name,
    rollNumber: result.roll_number,
    score: score,
    total: answerKey.length,
    percentage: (score / answerKey.length * 100).toFixed(2)
  };
}
```

---

Need help? Check [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for deployment instructions.

