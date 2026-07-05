import requests
import json
import os

# API base URL.
BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health check endpoint."""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_upload(image_path):
    """Test file upload."""
    print("📤 Testing file upload...")
    filename = os.path.basename(image_path)  # Use only the filename, without its directory.
    with open(image_path, 'rb') as f:
        files = {'file': (filename, f, 'image/jpeg')}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}\n")
    return response.json()

def test_ocr(image_path):
    """Test OCR processing."""
    print("🔍 Testing OCR...")
    filename = os.path.basename(image_path)
    with open(image_path, 'rb') as f:
        files = {'file': (filename, f, 'image/jpeg')}
        response = requests.post(f"{BASE_URL}/ocr", files=files)
    
    print(f"Status code: {response.status_code}")
    result = response.json()
    print(f"Success: {result['success']}")
    print(f"Recognized text: {result['text']}")
    print(f"Confidence: {result.get('confidence', 0):.2f}\n")
    return result

def test_process_note(image_path, context=None):
    """Test the complete note-processing flow."""
    print("🚀 Testing the complete note-processing flow...")
    
    filename = os.path.basename(image_path)
    with open(image_path, 'rb') as f:
        files = {'file': (filename, f, 'image/jpeg')}
        data = {}
        if context:
            data['additional_context'] = context
        
        response = requests.post(
            f"{BASE_URL}/process-note",
            files=files,
            data=data
        )
    
    print(f"Status code: {response.status_code}")
    result = response.json()
    
    print(f"Success: {result['success']}")
    print(f"Processing time: {result['processing_time']:.2f} seconds")
    
    if result['success']:
        print("\n📝 Original OCR text (first 200 characters):")
        print(result['original_text'][:200])
        print("\n✨ Formatted note:")
        print(result['formatted_note'])
    else:
        print(f"Error: {result['error']}")
    
    return result

if __name__ == "__main__":
    # Replace this with the path to your test image.
    test_image = "test_pictures/cs229_0.png"
    
    print("=" * 50)
    print("API tests started")
    print("=" * 50 + "\n")
    
    # 1. Health check.
    test_health()
    
    # 2. Upload test.
    test_upload(test_image)
    
    # # 3. OCR test.
    # test_ocr(test_image)
    
    # # 4. Complete processing-flow test.
    # test_process_note(test_image, context="This is the first machine learning lecture.")
    
    print("\n" + "=" * 50)
    print("Tests completed")
    print("=" * 50)
