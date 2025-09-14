# 硅基流动图片识别工具使用指南

## 🚀 简介

这是一个基于硅基流动(SiliconFlow)平台的多模态大模型图片识别工具，支持多种国产大模型进行图片理解和分析。

## ✨ 主要功能

- 🤖 **多模型支持**: 通义千问VL、DeepSeek VL、Yi VL、GLM-4V等
- 🌤️ **天气图片专业分析**: 专门针对天气图片的智能分析
- 📊 **结构化数据提取**: 自动提取温度、湿度、风力等天气信息
- 🔧 **易于配置**: 简单的环境配置即可使用
- 💾 **结果保存**: 自动保存分析结果为JSON格式

## 📦 安装依赖

```bash
# 安装基础依赖
pip install requests pillow

# 安装环境变量管理工具（可选）
pip install python-dotenv
```

## 🔑 配置API密钥

### 方法一：环境变量
```bash
export SILICONFLOW_API_KEY=your_api_key_here
```

### 方法二：.env文件
1. 复制配置文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入您的API密钥：
```
SILICONFLOW_API_KEY=your_siliconflow_api_key_here
DEFAULT_MODEL=qwen-vl-max
```

### 获取API密钥
1. 访问 [硅基流动官网](https://cloud.siliconflow.cn/)
2. 注册并登录账户
3. 在控制台中获取API密钥

## 🛠️ 使用方法

### 1. 运行配置向导
```bash
python3 setup_siliconflow.py
```

### 2. 基本使用
```bash
python3 siliconflow_image_recognition.py
```

### 3. 程序化使用
```python
from siliconflow_image_recognition import SiliconFlowImageRecognitionTool

# 初始化工具
recognizer = SiliconFlowImageRecognitionTool("your_api_key")

# 分析图片
result = recognizer.comprehensive_weather_analysis("weather_image.jpg")

print(result["analysis_report"])
```

## 🤖 支持的模型

| 模型ID | 模型名称 | 特点 | 适用场景 |
|--------|----------|------|----------|
| qwen-vl-max | 通义千问VL Max | 最强图片理解能力 | 复杂场景、高精度需求 |
| qwen-vl-plus | 通义千问VL Plus | 性能均衡 | 日常使用、快速响应 |
| deepseek-vl | DeepSeek VL | 中文理解优秀 | 中文图片、文档识别 |
| yi-vl | Yi VL | 多场景适应 | 通用图片理解 |
| glm-4v | GLM-4V | 中文理解强 | 中文场景、快速响应 |
| minicpm-v | MiniCPM-V | 轻量高效 | 成本敏感场景 |

## 📊 分析功能

### 天气图片分析
- 📍 **地点识别**: 自动识别城市和地区
- 🌡️ **温度提取**: 当前温度、最高/最低温度
- ☀️ **天气状况**: 晴天、阴天、雨天等
- 💧 **湿度信息**: 相对湿度百分比
- 💨 **风力数据**: 风速、风向、风力等级
- 🔽 **气压信息**: 大气压力数值
- 🌬️ **空气质量**: PM2.5、PM10等
- ☀️ **紫外线指数**: UV强度等级

### 通用图片识别
- 🔤 **文字识别**: OCR文字提取
- 🏷️ **内容分类**: 图片类型自动分类
- 📝 **内容描述**: 自然语言描述图片内容
- ❓ **问答交互**: 针对图片内容提问

## 📁 文件结构

```
├── siliconflow_image_recognition.py    # 主要识别工具
├── setup_siliconflow.py                # 配置向导
├── .env.example                         # 环境变量示例
├── README_siliconflow.md               # 使用说明（本文件）
└── analysis_results/                   # 分析结果目录
```

## 💡 使用示例

### 分析天气截图
```python
# 分析天气应用截图
result = recognizer.comprehensive_weather_analysis(
    "weather_app_screenshot.png",
    model="qwen-vl-max"
)

# 获取结构化天气数据
weather_data = result["extracted_weather_data"]
print(f"温度: {weather_data.get('temperature', [])}")
print(f"湿度: {weather_data.get('humidity', [])}")
print(f"天气状况: {weather_data.get('weather_condition', [])}")
```

### 通用图片理解
```python
# 通用图片分析
result = recognizer.recognize_with_siliconflow(
    "image.jpg",
    "请详细描述这张图片的内容和主要信息",
    model="deepseek-vl"
)

print(result["content"])
```

## 🔧 高级配置

### 自定义提示词
```python
# 自定义分析提示词
custom_prompt = """
请分析这张图片，重点关注：
1. 图片中的主要对象和场景
2. 文字内容和数字信息
3. 颜色和视觉特征
4. 整体氛围和情感表达
"""

result = recognizer.recognize_with_siliconflow(
    "image.jpg",
    custom_prompt
)
```

### 批量处理
```python
import os

# 批量处理目录中的所有图片
image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
for filename in os.listdir('.'):
    if any(filename.lower().endswith(ext) for ext in image_extensions):
        print(f"处理: {filename}")
        result = recognizer.comprehensive_weather_analysis(filename)
        
        # 保存结果
        output_file = f"result_{filename}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
```

## ⚠️ 注意事项

1. **API限制**: 请注意硅基流动API的调用限制和费用
2. **图片大小**: 建议图片大小不超过10MB
3. **格式支持**: 支持JPG、PNG、GIF、BMP、WebP等格式
4. **网络连接**: 需要稳定的网络连接访问API
5. **隐私安全**: 注意不要上传敏感或私密的图片

## 🐛 故障排除

### 常见问题

1. **API密钥错误**
   ```
   检查SILICONFLOW_API_KEY环境变量是否正确设置
   ```

2. **网络连接失败**
   ```
   检查网络连接和防火墙设置
   确认可以访问 api.siliconflow.cn
   ```

3. **模型调用失败**
   ```
   确认模型名称正确
   检查API账户余额
   ```

4. **图片格式不支持**
   ```
   将图片转换为JPG或PNG格式
   确保图片文件没有损坏
   ```

### 调试模式
```bash
# 启用详细日志
export PYTHONPATH=.
python3 -v siliconflow_image_recognition.py
```

## 📞 技术支持

- **硅基流动官方文档**: https://docs.siliconflow.cn/
- **API支持**: support@siliconflow.cn
- **问题反馈**: 在GitHub Issues中提交问题

## 🔄 更新日志

### v1.0.0 (2025-09-10)
- ✨ 初始版本发布
- 🤖 支持6种国产多模态模型
- 🌤️ 天气图片专业分析功能
- 📊 结构化数据提取
- 💾 分析结果保存

## 📄 许可证

本项目基于MIT许可证开源。

## 🙏 致谢

感谢硅基流动平台提供强大的多模态AI能力！