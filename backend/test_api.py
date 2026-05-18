import requests
import json
import os

# API 基础 URL
BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}\n")

def test_upload(image_path):
    """测试文件上传"""
    print("📤 测试文件上传...")
    filename = os.path.basename(image_path)  # 只使用文件名，不包括目录
    with open(image_path, 'rb') as f:
        files = {'file': (filename, f, 'image/jpeg')}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}\n")
    return response.json()

def test_ocr(image_path):
    """测试 OCR"""
    print("🔍 测试 OCR 识别...")
    filename = os.path.basename(image_path)
    with open(image_path, 'rb') as f:
        files = {'file': (filename, f, 'image/jpeg')}
        response = requests.post(f"{BASE_URL}/ocr", files=files)
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"成功: {result['success']}")
    print(f"识别的文本: {result['text']}")
    print(f"置信度: {result.get('confidence', 0):.2f}\n")
    return result

def test_process_note(image_path, context=None):
    """测试完整的笔记处理"""
    print("🚀 测试完整笔记处理流程...")
    
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
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    
    print(f"成功: {result['success']}")
    print(f"处理时间: {result['processing_time']:.2f} 秒")
    
    if result['success']:
        print("\n📝 原始 OCR 文本（前200字符）:")
        print(result['original_text'][:200])
        print("\n✨ 整理后的笔记:")
        print(result['formatted_note'])
    else:
        print(f"错误: {result['error']}")
    
    return result

if __name__ == "__main__":
    # 替换为你的测试图片路径
    test_image = "test_pictures/cs229_0.png"
    
    print("=" * 50)
    print("API 测试开始")
    print("=" * 50 + "\n")
    
    # 1. 健康检查
    test_health()
    
    # 2. 上传测试
    test_upload(test_image)
    
    # # 3. OCR 测试
    # test_ocr(test_image)
    
    # # 4. 完整流程测试
    # test_process_note(test_image, context="这是机器学习课程的第一讲")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)