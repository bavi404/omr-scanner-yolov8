"""
Download trained model from URL
Run during Render deployment build phase
"""

import os
import requests
from pathlib import Path

def download_file(url, destination):
    """Download file from URL with progress"""
    print(f"Downloading model from: {url}")
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    block_size = 8192
    downloaded = 0
    
    with open(destination, 'wb') as f:
        for chunk in response.iter_content(chunk_size=block_size):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\rProgress: {percent:.1f}%", end='', flush=True)
    
    print(f"\n✅ Model downloaded to: {destination}")
    print(f"   Size: {os.path.getsize(destination) / (1024*1024):.2f} MB")

def main():
    """Main download function"""
    # Get model URL from environment variable
    model_url = os.environ.get('MODEL_DOWNLOAD_URL')
    
    if not model_url:
        print("⚠️  MODEL_DOWNLOAD_URL not set. Skipping model download.")
        print("   You can:")
        print("   1. Set MODEL_DOWNLOAD_URL environment variable in Render")
        print("   2. Or manually upload model file")
        return
    
    # Download destination
    model_path = os.environ.get('MODEL_PATH', 'best.pt')
    
    # Check if model already exists
    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024*1024)
        print(f"✓ Model already exists: {model_path} ({size_mb:.2f} MB)")
        return
    
    # Download model
    try:
        download_file(model_url, model_path)
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        print("\nPlease ensure:")
        print("1. MODEL_DOWNLOAD_URL is a direct download link")
        print("2. The file is accessible publicly")
        print("3. For Google Drive, use: https://drive.google.com/uc?export=download&id=FILE_ID")
        raise

if __name__ == '__main__':
    main()

