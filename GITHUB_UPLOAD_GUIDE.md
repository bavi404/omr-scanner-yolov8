# 📤 GitHub Upload Guide

## ✅ What TO Upload to GitHub

Upload these files:
```
✅ Source Code
   - omr_processor.py
   - api_server.py
   - test.py
   - app.py
   - batch_process.py

✅ Configuration
   - data.yaml (without images)
   - requirements.txt
   - Procfile
   - .gitignore

✅ Documentation
   - DEPLOYMENT_GUIDE.md
   - QUICK_DEPLOY.md
   - HOW_TO_RUN.md (if created)
   - README.md (if created)
   - frontend_example.html

✅ Folder Structure (empty folders)
   - train/
   - valid/
   - test/
```

---

## ❌ What NOT to Upload to GitHub

### **1. Model Weights (*.pt files) - TOO LARGE**
```
❌ best.pt (your trained model)
❌ yolov8s.pt (22MB)
❌ Any *.pt or *.pth files
```

**Why?** Model files are usually 20MB-500MB+, GitHub has 100MB limit per file.

**Solution:** Host models separately (see below)

---

### **2. Dataset Images - TOO LARGE**
```
❌ train/images/*.jpg (100s of images)
❌ valid/images/*.jpg
❌ test/images/*.jpg
```

**Why?** Hundreds of images = GBs of data

**Solution:** Host dataset separately (see below)

---

### **3. Uploaded & Temporary Files**
```
❌ uploads/
❌ api_uploads/
❌ batch_results/
❌ omr_output.json
❌ *_annotated.jpg
❌ temp files
```

**Why?** Generated files, not part of source code

---

### **4. Environment Files & Secrets**
```
❌ .env
❌ *.key
❌ *.pem
❌ secrets.json
❌ API keys
❌ Passwords
```

**Why?** SECURITY - Never upload secrets!

---

### **5. Python Cache & Virtual Environments**
```
❌ __pycache__/
❌ venv/
❌ *.pyc
❌ .env/
```

**Why?** Generated files, can be recreated

---

## 🌐 Where to Host Large Files

### **Option 1: Host Model Weights**

#### **A. Google Drive (Easiest)**
1. Upload `best.pt` to Google Drive
2. Make it publicly accessible
3. Get shareable link
4. In your code, download it:

```python
import gdown

# Download model from Google Drive
MODEL_URL = 'https://drive.google.com/uc?id=YOUR_FILE_ID'
gdown.download(MODEL_URL, 'best.pt', quiet=False)
```

#### **B. Hugging Face Hub (Recommended for ML)**
```bash
# Install
pip install huggingface_hub

# Upload model
from huggingface_hub import HfApi
api = HfApi()
api.upload_file(
    path_or_fileobj="best.pt",
    path_in_repo="best.pt",
    repo_id="your-username/omr-model",
    repo_type="model",
)
```

Download in code:
```python
from huggingface_hub import hf_hub_download

model_path = hf_hub_download(
    repo_id="your-username/omr-model",
    filename="best.pt"
)
```

#### **C. AWS S3 (Professional)**
```bash
# Upload
aws s3 cp best.pt s3://your-bucket/models/best.pt --acl public-read

# URL: https://your-bucket.s3.amazonaws.com/models/best.pt
```

#### **D. GitHub Releases (If < 100MB)**
1. Go to your GitHub repo
2. Releases → Create new release
3. Attach `best.pt` as release asset
4. Download via URL in code

---

### **Option 2: Host Dataset**

#### **For Roboflow Dataset:**
Keep it on Roboflow and download via API:
```python
from roboflow import Roboflow

rf = Roboflow(api_key="YOUR_API_KEY")
project = rf.workspace().project("omr-mcqs-dataset")
dataset = project.version(1).download("yolov8")
```

#### **For Custom Dataset:**
- Upload to Google Drive / Dropbox
- Use Kaggle Datasets (free)
- Use AWS S3 / Google Cloud Storage

---

## 📋 Step-by-Step: Prepare for GitHub

### **Step 1: Check File Sizes**
```bash
# See large files
du -sh * | sort -hr | head -20

# Or on Windows PowerShell:
Get-ChildItem | Sort-Object Length -Descending | Select-Object Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB,2)}} | Select-Object -First 20
```

### **Step 2: Move Large Files**
```bash
# Create backup folder
mkdir ../model_backup
mv *.pt ../model_backup/
mv train/images/* ../dataset_backup/train/
mv valid/images/* ../dataset_backup/valid/
mv test/images/* ../dataset_backup/test/
```

### **Step 3: Initialize Git**
```bash
# Initialize repository
git init

# Check what will be uploaded
git status

# The .gitignore should exclude large files
```

### **Step 4: Commit & Push**
```bash
git add .
git commit -m "Initial commit: OMR processing system"

# Create GitHub repo and push
git remote add origin https://github.com/your-username/omr-processor.git
git branch -M main
git push -u origin main
```

---

## 🔒 Security Checklist Before Upload

- [ ] No API keys in code
- [ ] No passwords or tokens
- [ ] No `.env` files
- [ ] No private keys (*.pem, *.key)
- [ ] Model path is configurable (not hardcoded)
- [ ] No personal information
- [ ] No database credentials

---

## 📝 Update Your Code for Deployment

### **1. Make Model Path Configurable**

Update `api_server.py`:
```python
import os

# Use environment variable or default path
MODEL_PATH = os.getenv('MODEL_PATH', r"C:\Users\sanka\runs\detect\train3\weights\best.pt")

# Or download from URL
MODEL_URL = os.getenv('MODEL_URL', 'https://your-storage-url/best.pt')

# Download model if not exists
if not os.path.exists('best.pt') and MODEL_URL:
    import requests
    print("Downloading model...")
    r = requests.get(MODEL_URL)
    with open('best.pt', 'wb') as f:
        f.write(r.content)
    MODEL_PATH = 'best.pt'
```

### **2. Add Instructions to README**

Create `README.md`:
```markdown
# OMR Processing System

## Setup

1. Install dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

2. Download model weights:
   - Download from: [Google Drive Link]
   - Place in project root as `best.pt`

3. Run API:
   \`\`\`bash
   python api_server.py
   \`\`\`

## Model Weights
Model weights are not included due to size. Download from:
- **Google Drive**: [Your Link]
- **Hugging Face**: [Your Link]

\`\`\`
```

---

## 📦 Final GitHub Repository Structure

```
your-repo/
├── .gitignore                    ✅ Upload
├── README.md                     ✅ Upload
├── requirements.txt              ✅ Upload
├── Procfile                      ✅ Upload
├── DEPLOYMENT_GUIDE.md           ✅ Upload
├── QUICK_DEPLOY.md              ✅ Upload
├── GITHUB_UPLOAD_GUIDE.md       ✅ Upload
├── data.yaml                     ✅ Upload
├── omr_processor.py              ✅ Upload
├── api_server.py                 ✅ Upload
├── test.py                       ✅ Upload
├── app.py                        ✅ Upload
├── batch_process.py              ✅ Upload
├── frontend_example.html         ✅ Upload
├── train/                        ✅ Upload (empty folder)
├── valid/                        ✅ Upload (empty folder)
├── test/                         ✅ Upload (empty folder)
│   └── README.md                ✅ "Place images here"
│
├── best.pt                       ❌ DON'T UPLOAD (host separately)
├── yolov8s.pt                    ❌ DON'T UPLOAD
├── uploads/                      ❌ DON'T UPLOAD (in .gitignore)
├── venv/                         ❌ DON'T UPLOAD (in .gitignore)
└── __pycache__/                  ❌ DON'T UPLOAD (in .gitignore)
```

---

## ✅ Quick Checklist

Before pushing to GitHub:

1. [ ] Created `.gitignore` file
2. [ ] Moved model weights to cloud storage
3. [ ] Removed all `.jpg`/`.png` dataset images
4. [ ] No secrets or API keys in code
5. [ ] Made paths configurable with environment variables
6. [ ] Created README with model download instructions
7. [ ] Tested that code runs without local files
8. [ ] Checked repository size (should be < 50MB)

---

## 🚀 After Upload

Tell your friend:

1. **Clone repo:**
   ```bash
   git clone https://github.com/your-username/omr-processor.git
   cd omr-processor
   ```

2. **Download model:**
   ```bash
   # From your shared Google Drive link
   # Place as best.pt in project root
   ```

3. **Install & run:**
   ```bash
   pip install -r requirements.txt
   python api_server.py
   ```

---

## 💡 Pro Tip

Use **Git LFS** (Large File Storage) for files 50-100MB:

```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.pt"
git add .gitattributes
git commit -m "Configure LFS"

# Now you can commit model files
git add best.pt
git commit -m "Add model weights via LFS"
```

**Note:** GitHub has 1GB LFS storage limit on free tier.

---

## 📞 Need Help?

If GitHub rejects your push:
- Check file sizes: files over 100MB will fail
- Check total repo size: shouldn't exceed 1GB
- Use `.gitignore` to exclude large files
- Host models separately on cloud storage

**Your code is ready for GitHub! 🎉**

