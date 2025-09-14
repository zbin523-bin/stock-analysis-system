# 图片识别和理解功能配置

## 方案一：集成外部OCR服务

### 1. 安装依赖
```bash
pip install openai requests Pillow python-dotenv
```

### 2. 配置环境变量
创建 `.env` 文件：
```
OPENAI_API_KEY=your_openai_api_key_here
BAIDU_OCR_API_KEY=your_baidu_ocr_key_here
BAIDU_OCR_SECRET_KEY=your_baidu_ocr_secret_here
```

### 3. 使用方法

#### 基本图片识别
```python
from image_recognition_tool import ImageRecognitionTool

recognizer = ImageRecognitionTool()
result = recognizer.extract_text_from_image("your_image.jpg")
print(result["content"])
```

#### 图片理解
```python
result = recognizer.understand_image(
    "your_image.jpg", 
    "这张图片中有什么天气信息？"
)
print(result["answer"])
```

## 方案二：集成到Claude Code

### 1. 创建自定义工具
将 `image_recognition_tool.py` 放到你的项目目录中

### 2. 在Claude Code中使用
```bash
# 在Claude Code中调用Python脚本
python image_recognition_tool.py
```

### 3. 创建MCP服务器
使用 `image_recognition_mcp.py` 创建一个MCP服务器，为Claude Code提供图片识别能力

## 方案三：使用命令行工具

### 1. 创建脚本
```bash
#!/bin/bash
# recognize_image.sh

python3 -c "
from image_recognition_tool import ImageRecognitionTool
import sys
import json

recognizer = ImageRecognitionTool()
image_path = '$1'
question = '$2'

if question:
    result = recognizer.understand_image(image_path, question)
else:
    result = recognizer.extract_text_from_image(image_path)

print(json.dumps(result, ensure_ascii=False, indent=2))
"
```

### 2. 使用脚本
```bash
# 基本识别
./recognize_image.sh weather.jpg

# 带问题识别
./recognize_image.sh weather.jpg "这是什么天气？"
```

## 方案四：使用Web服务

### 1. 创建Flask应用
```python
from flask import Flask, request, jsonify
from image_recognition_tool import ImageRecognitionTool
import base64
import tempfile
import os

app = Flask(__name__)
recognizer = ImageRecognitionTool()

@app.route('/recognize', methods=['POST'])
def recognize():
    data = request.json
    image_data = data.get('image')
    question = data.get('question', '')
    
    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
        tmp.write(base64.b64decode(image_data))
        tmp_path = tmp.name
    
    try:
        if question:
            result = recognizer.understand_image(tmp_path, question)
        else:
            result = recognizer.extract_text_from_image(tmp_path)
        
        return jsonify(result)
    finally:
        os.unlink(tmp_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### 2. 启动服务
```bash
pip install flask
python app.py
```

## 支持的图片格式
- JPEG/JPG
- PNG
- GIF
- BMP
- WebP

## 使用建议

1. **天气图片识别**：使用专门的天气分析提示词
2. **文档OCR**：使用高分辨率图片，确保文字清晰
3. **图表分析**：提供具体的问题，如"这个图表显示了什么趋势？"
4. **实时处理**：对于大量图片，建议使用异步处理

## 错误处理

常见错误及解决方案：
- API密钥错误：检查环境变量配置
- 图片格式不支持：转换为JPEG格式
- 图片过大：压缩图片或使用分块处理
- 网络超时：增加重试机制

## 扩展功能

1. **批量处理**：支持多图片同时识别
2. **结果缓存**：避免重复识别相同图片
3. **自定义模型**：集成本地OCR模型
4. **多语言支持**：识别不同语言的文字