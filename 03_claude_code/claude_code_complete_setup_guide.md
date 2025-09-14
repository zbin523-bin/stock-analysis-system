# Claude Code 完整配置与使用指南

## 1. 搜索功能问题解决方案

### 1.1 检查当前状态
首先检查Claude Code的当前状态：

```bash
# 检查Claude CLI版本
claude --version

# 检查认证状态
claude auth status

# 检查配置文件
ls -la ~/.anthropic/
ls -la ~/.config/claude/
```

### 1.2 重新配置认证
如果认证有问题，重新配置：

```bash
# 退出当前认证
claude auth logout

# 重新登录
claude auth login
```

### 1.3 配置文件优化
创建或更新配置文件：

```bash
# 创建配置目录
mkdir -p ~/.config/claude
mkdir -p ~/.anthropic

# 创建配置文件
cat > ~/.config/claude/config.json << EOF
{
  "model": "claude-3-5-sonnet-20241022",
  "max_tokens": 4000,
  "temperature": 0.1,
  "timeout": 30000,
  "auto_save": true,
  "backup_count": 5
}
EOF
```

## 2. 环境变量配置

### 2.1 设置必要的环境变量
在你的shell配置文件中添加（~/.zshrc 或 ~/.bashrc）：

```bash
# Claude Code 相关环境变量
export ANTHROPIC_API_KEY="your_api_key_here"
export CLAUDE_CONFIG_DIR="$HOME/.config/claude"
export CLAUDE_TEMPLATES_DIR="$HOME/.config/claude/templates"

# 优化Claude Code性能
export CLAUDE_MAX_TOKENS=4000
export CLAUDE_TIMEOUT=30000
export CLAUDE_MODEL="claude-3-5-sonnet-20241022"
```

### 2.2 加载配置
```bash
# 重新加载配置
source ~/.zshrc
# 或者
source ~/.bashrc
```

## 3. 推荐的插件和工具

### 3.1 开发工具集成
```bash
# 安装Node.js相关工具
npm install -g @anthropic-ai/claude-cli

# 安装Python相关工具
pip install anthropic

# 安装其他有用的工具
brew install jq
brew install yq
```

### 3.2 VS Code插件
如果你使用VS Code，推荐安装以下插件：

```bash
# 安装VS Code插件
code --install-extension amazonwebservices.amazon-q-cli
code --install-extension ms-python.python
code --install-extension ms-vscode.vscode-json
code --install-extension yzhang.markdown-all-in-one
code --install-extension ms-vscode.vscode-yaml
```

## 4. 工作流程优化

### 4.1 创建项目模板系统
```bash
# 创建模板目录
mkdir -p ~/.config/claude/templates

# 创建常用模板
# (模板内容见之前的setup-claude-code.sh脚本)
```

### 4.2 自动化脚本
创建一些常用的自动化脚本：

```bash
# 创建脚本目录
mkdir -p ~/bin

# 创建claude-helper脚本
cat > ~/bin/claude-helper << 'EOF'
#!/bin/bash

# Claude Code 助手脚本

case "$1" in
    "setup")
        echo "设置Claude Code环境..."
        # 设置逻辑
        ;;
    "search")
        echo "搜索功能替代方案..."
        # 使用curl或其他工具进行搜索
        ;;
    "export")
        echo "导出Claude Code配置..."
        # 导出配置
        ;;
    *)
        echo "用法: claude-helper {setup|search|export}"
        ;;
esac
EOF

chmod +x ~/bin/claude-helper
```

## 5. 搜索功能替代方案

如果Claude Code的搜索功能有问题，可以使用以下替代方案：

### 5.1 使用curl进行API调用
```bash
# 创建搜索脚本
cat > ~/bin/claude-search << 'EOF'
#!/bin/bash

# Claude Code 搜索功能替代方案

if [ -z "$1" ]; then
    echo "请提供搜索关键词"
    exit 1
fi

QUERY="$1"
API_KEY="${ANTHROPIC_API_KEY}"

if [ -z "$API_KEY" ]; then
    echo "请设置 ANTHROPIC_API_KEY 环境变量"
    exit 1
fi

curl -X POST "https://api.anthropic.com/v1/messages" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 4000,
    "messages": [
      {
        "role": "user",
        "content": "请搜索以下内容：'"$QUERY"'"
      }
    ]
  }'
EOF

chmod +x ~/bin/claude-search
```

### 5.2 使用Python脚本
```python
#!/usr/bin/env python3
# claude-search-python.py

import os
import requests
import json
import sys

def claude_search(query):
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("请设置 ANTHROPIC_API_KEY 环境变量")
        return
    
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    data = {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 4000,
        "messages": [
            {
                "role": "user",
                "content": f"请搜索以下内容：{query}"
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        print(result['content'][0]['text'])
    except Exception as e:
        print(f"搜索失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python claude-search-python.py <搜索关键词>")
        sys.exit(1)
    
    query = ' '.join(sys.argv[1:])
    claude_search(query)
```

## 6. 完整的配置文件

### 6.1 ~/.config/claude/config.json
```json
{
  "model": "claude-3-5-sonnet-20241022",
  "max_tokens": 4000,
  "temperature": 0.1,
  "timeout": 30000,
  "auto_save": true,
  "backup_count": 5,
  "templates": {
    "project": "~/.config/claude/templates/project-plan.md",
    "meeting": "~/.config/claude/templates/meeting-notes.md",
    "review": "~/.config/claude/templates/code-review.md"
  },
  "workflows": {
    "plan": "项目规划工作流",
    "code": "代码开发工作流",
    "review": "代码审查工作流",
    "test": "测试工作流",
    "doc": "文档生成工作流"
  }
}
```

### 6.2 ~/.config/claude/aliases.json
```json
{
  "常用命令": {
    "help": "claude help",
    "chat": "claude chat",
    "code": "claude code",
    "config": "claude config"
  },
  "项目相关": {
    "init": "claude-init",
    "plan": "claude-workflow plan",
    "dev": "claude-workflow code",
    "test": "claude-workflow test"
  },
  "学习相关": {
    "learn": "claude-learn",
    "study": "claude-learn"
  },
  "会议相关": {
    "daily": "claude-meeting daily",
    "review": "claude-meeting review",
    "planning": "claude-meeting planning"
  }
}
```

## 7. 故障排除

### 7.1 常见问题
1. **认证问题**
   ```bash
   # 重新认证
   claude auth logout
   claude auth login
   ```

2. **配置文件问题**
   ```bash
   # 重置配置
   rm -rf ~/.config/claude
   mkdir -p ~/.config/claude
   ```

3. **网络问题**
   ```bash
   # 检查网络连接
   ping api.anthropic.com
   
   # 检查代理设置
   echo $HTTP_PROXY
   echo $HTTPS_PROXY
   ```

### 7.2 性能优化
```bash
# 优化Claude Code性能
export CLAUDE_MAX_TOKENS=2000  # 减少token数量
export CLAUDE_TIMEOUT=60000    # 增加超时时间
export CLAUDE_TEMPERATURE=0.1  # 降低温度以提高一致性
```

## 8. 最佳实践

### 8.1 使用技巧
1. **明确的指令**：提供清晰、具体的指令
2. **上下文信息**：提供充分的背景信息
3. **分步骤**：将复杂任务分解为简单步骤
4. **定期保存**：定期保存重要的对话和结果

### 8.2 安全考虑
1. **敏感信息**：不要分享敏感信息
2. **API密钥**：妥善保管API密钥
3. **数据验证**：验证生成内容的准确性
4. **备份重要数据**：定期备份重要的配置和数据

## 9. 更新和维护

### 9.1 定期更新
```bash
# 更新Claude CLI
npm update -g @anthropic-ai/claude-cli

# 更新配置
# 定期检查并更新配置文件
```

### 9.2 备份配置
```bash
# 备份配置文件
cp -r ~/.config/claude ~/.config/claude.backup.$(date +%Y%m%d)
cp -r ~/.anthropic ~/.anthropic.backup.$(date +%Y%m%d)
```

---

*这份指南将帮助你更好地配置和使用Claude Code，解决搜索功能等问题，并提供完整的工作流程支持。*