#!/bin/bash

# Claude Code 优化配置脚本
# 这个脚本将帮助你配置Claude Code和相关工具

echo "开始配置Claude Code工作环境..."

# 检查并安装必要的工具
echo "检查必要的工具..."

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "安装Node.js..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
    source ~/.bashrc
    nvm install 18
    nvm use 18
fi

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "安装Python..."
    brew install python3
fi

# 检查Git
if ! command -v git &> /dev/null; then
    echo "安装Git..."
    brew install git
fi

# 创建Claude Code配置目录
mkdir -p ~/.config/claude
mkdir -p ~/.anthropic

# 创建Claude Code配置文件
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

# 创建常用的Claude Code别名和函数
cat >> ~/.zshrc << 'EOF'

# Claude Code 别名和函数
alias claude-help='echo "Claude Code 常用命令：
- claude chat: 开始对话
- claude code: 代码助手
- claude help: 帮助信息
- claude config: 配置管理"'

# Claude Code 项目初始化函数
claude-init() {
    local project_name=$1
    if [ -z "$project_name" ]; then
        echo "请提供项目名称"
        return 1
    fi
    
    mkdir -p "$project_name"
    cd "$project_name"
    
    # 创建项目结构
    mkdir -p docs src tests
    
    # 创建Claude Code项目配置
    cat > .claude.md << EOF
# Claude Code 项目配置

## 项目信息
项目名称: $project_name
创建时间: $(date)
项目类型: 通用项目

## 使用场景
- 代码开发
- 文档生成
- 测试编写
- 项目规划

## 注意事项
- 定期备份重要文件
- 遵循公司代码规范
- 及时更新依赖项
EOF
    
    echo "项目 $project_name 初始化完成"
}

# Claude Code 工作流函数
claude-workflow() {
    local workflow_type=$1
    case $workflow_type in
        "plan")
            echo "启动项目规划工作流..."
            claude "我需要规划一个新项目，请帮我制定详细的项目计划，包括目标、任务分解、时间估算等"
            ;;
        "code")
            echo "启动代码开发工作流..."
            claude "我需要开发新功能，请帮我生成代码框架和实现方案"
            ;;
        "review")
            echo "启动代码审查工作流..."
            claude "请帮我审查这段代码，提供改进建议和最佳实践"
            ;;
        "test")
            echo "启动测试工作流..."
            claude "请帮我为这个功能编写测试用例"
            ;;
        "doc")
            echo "启动文档生成工作流..."
            claude "请帮我为这个项目生成技术文档"
            ;;
        *)
            echo "可用的工作流类型：plan, code, review, test, doc"
            ;;
    esac
}

# Claude Code 学习助手
claude-learn() {
    local topic=$1
    if [ -z "$topic" ]; then
        echo "请提供学习主题"
        return 1
    fi
    
    echo "开始学习 $topic ..."
    claude "我想要学习 $topic，请为我制定学习计划，包括：
1. 核心概念和原理
2. 实践项目建议
3. 推荐学习资源
4. 常见问题和解决方案"
}

# Claude Code 会议助手
claude-meeting() {
    local meeting_type=$1
    case $meeting_type in
        "daily")
            claude "请帮我准备每日站会的内容，包括：
1. 昨天完成的工作
2. 今天计划的工作
3. 遇到的问题和需要的帮助"
            ;;
        "review")
            claude "请帮我准备项目 review 会议的内容，包括：
1. 项目进展汇报
2. 关键指标分析
3. 风险和问题
4. 下一步计划"
            ;;
        "planning")
            claude "请帮我准备项目规划会议的内容，包括：
1. 项目目标讨论
2. 任务分解
3. 资源分配
4. 时间安排"
            ;;
        *)
            echo "可用的会议类型：daily, review, planning"
            ;;
    esac
}
EOF

# 创建Claude Code模板目录
mkdir -p ~/.config/claude/templates

# 创建常用模板
cat > ~/.config/claude/templates/project-plan.md << 'EOF'
# 项目计划模板

## 项目概述
- **项目名称**: 
- **项目目标**: 
- **项目周期**: 
- **团队成员**: 

## 任务分解
### 阶段一：需求分析
- [ ] 
- [ ] 
- [ ] 

### 阶段二：设计开发
- [ ] 
- [ ] 
- [ ] 

### 阶段三：测试部署
- [ ] 
- [ ] 
- [ ] 

## 时间安排
| 任务 | 开始时间 | 结束时间 | 负责人 | 状态 |
|------|----------|----------|--------|------|
|      |          |          |        |      |

## 风险评估
| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
|      |        |      |          |

## 成功标准
- [ ] 
- [ ] 
- [ ] 
EOF

cat > ~/.config/claude/templates/meeting-notes.md << 'EOF'
# 会议纪要模板

## 会议信息
- **会议主题**: 
- **会议时间**: 
- **参会人员**: 
- **会议记录人**: 

## 议程
1. 
2. 
3. 

## 讨论内容

### 议题1：
**讨论要点**:
**结论**:
**行动项**:

### 议题2：
**讨论要点**:
**结论**:
**行动项**:

## 决策事项

## 下一步行动
| 行动项 | 负责人 | 截止时间 | 状态 |
|--------|--------|----------|------|
|        |        |          |      |

## 下次会议
- **时间**: 
- **议题**: 
EOF

cat > ~/.config/claude/templates/code-review.md << 'EOF'
# 代码审查模板

## 代码信息
- **文件路径**: 
- **功能描述**: 
- **审查人**: 
- **审查时间**: 

## 整体评价
- **代码质量**: 
- **性能表现**: 
- **安全性**: 
- **可维护性**: 

## 具体建议

### 优点
- 

### 改进建议
- 

### 问题修复
- 

## 测试建议
- 

## 文档建议
- 

## 总体评价
- **推荐**: 是/否
- **评论**: 
EOF

# 安装有用的VS Code插件（如果使用VS Code）
if command -v code &> /dev/null; then
    echo "安装VS Code插件..."
    code --install-extension amazonwebservices.amazon-q-cli
    code --install-extension ms-python.python
    code --install-extension ms-vscode.vscode-json
    code --install-extension yzhang.markdown-all-in-one
fi

# 创建Claude Code使用指南
cat > ~/.config/claude/usage-guide.md << 'EOF'
# Claude Code 使用指南

## 基础配置
1. 确保已登录Claude账户
2. 配置API密钥（如果需要）
3. 设置合适的模型参数

## 常用命令
- `claude chat`: 开始对话
- `claude code`: 代码助手
- `claude help`: 帮助信息

## 工作流程
1. 项目初始化：`claude-init <project-name>`
2. 项目规划：`claude-workflow plan`
3. 代码开发：`claude-workflow code`
4. 代码审查：`claude-workflow review`
5. 测试编写：`claude-workflow test`
6. 文档生成：`claude-workflow doc`

## 学习助手
- `claude-learn <topic>`: 学习新主题
- `claude-meeting <type>`: 会议准备

## 最佳实践
1. 明确任务目标和要求
2. 提供充分的上下文信息
3. 分步骤复杂任务
4. 定期保存和备份重要内容
5. 遵循安全和隐私原则

## 注意事项
1. 不要分享敏感信息
2. 验证生成内容的准确性
3. 保持批判性思维
4. 定期更新知识和技能
EOF

echo "Claude Code 配置完成！"
echo ""
echo "使用方法："
echo "1. 重新加载终端配置：source ~/.zshrc"
echo "2. 查看使用指南：cat ~/.config/claude/usage-guide.md"
echo "3. 初始化项目：claude-init <project-name>"
echo "4. 启动工作流：claude-workflow <type>"
echo ""
echo "模板文件位置：~/.config/claude/templates/"
echo "配置文件位置：~/.config/claude/config.json"