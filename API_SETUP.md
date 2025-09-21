# API设置指南

## 🚀 快速开始

这个AI斗地主项目支持两种AI类型：

1. **算法AI**（默认）- 本地运行，无需配置
2. **LLM AI** - 需要配置API密钥

## 🤖 LLM AI 设置

### 1. 选择LLM提供商

#### OpenAI (推荐)
- **优点**: 响应快速，策略智能
- **模型**: gpt-4o-mini (推荐), gpt-4o
- **成本**: 低 (~$0.001/局)
- **官网**: https://openai.com

#### Anthropic (Claude)
- **优点**: 推理能力强，策略深度好
- **模型**: claude-3-haiku, claude-3-sonnet
- **成本**: 中等 (~$0.005/局)
- **官网**: https://anthropic.com

#### DeepSeek (性价比)
- **优点**: 成本最低，中文友好
- **模型**: deepseek-chat
- **成本**: 极低 (~$0.0001/局)
- **官网**: https://deepseek.com

#### Moonshot
- **优点**: 国内服务，稳定性好
- **模型**: moonshot-v1-8k
- **成本**: 低 (~$0.002/局)
- **官网**: https://moonshot.cn

### 2. 获取API密钥

1. 访问选择的提供商官网
2. 注册账号并完成实名认证
3. 进入API管理页面
4. 创建新的API密钥
5. 复制密钥（通常以`sk-`开头）

### 3. 配置环境变量

#### Windows (命令提示符)
```cmd
# 设置OpenAI
set OPENAI_API_KEY=sk-your-openai-key-here

# 或设置其他提供商
set ANTHROPIC_API_KEY=sk-ant-your-claude-key-here
set DEEPSEEK_API_KEY=sk-your-deepseek-key-here
set MOONSHOT_API_KEY=sk-your-moonshot-key-here
```

#### Windows (PowerShell)
```powershell
$env:OPENAI_API_KEY="sk-your-openai-key-here"
```

#### Linux/macOS
```bash
export OPENAI_API_KEY="sk-your-openai-key-here"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export OPENAI_API_KEY="sk-your-openai-key-here"' >> ~/.bashrc
echo 'export DEEPSEEK_API_KEY="sk-7d5a725ef8b54398b17bf6468dc2b674"' >> ~/.bashrc
source ~/.bashrc
```

#### 使用 .env 文件 (推荐)
创建 `.env` 文件（与main.py同目录）：
```env
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-claude-key-here
DEEPSEEK_API_KEY=sk-your-deepseek-key-here
MOONSHOT_API_KEY=sk-your-moonshot-key-here
```

### 4. 安装额外依赖

```bash
pip install aiohttp python-dotenv
```

### 5. 验证配置

运行配置检查：
```bash
python config.py
```

或在游戏中选择"AI类型设置"查看可用提供商。

## 🎮 使用LLM AI

### 启动增强版游戏
```bash
python main_with_llm.py
```

### 游戏中切换AI类型
1. 主菜单选择"AI类型设置"
2. 选择"使用LLM AI"
3. 选择提供商和模型

### 性能对比

| 特性 | 算法AI | LLM AI |
|------|--------|--------|
| 响应速度 | 毫秒级 | 1-5秒 |
| 策略复杂度 | 中等 | 很高 |
| 趣味性 | 中等 | 很高 |
| 成本 | 免费 | 低成本 |
| 网络要求 | 无 | 需要 |

## 🔧 高级配置

### 自定义模型参数
编辑 `config.py` 文件：
```python
LLM_CONFIGS = {
    "openai": {
        "models": {
            "fast": "gpt-4o-mini",      # 快速模式
            "smart": "gpt-4o",          # 智能模式
            "cheap": "gpt-3.5-turbo"    # 经济模式
        }
    }
}
```

### 调整AI行为
在 `config.py` 中修改：
```python
GAME_CONFIG = {
    "max_thinking_time": 5.0,       # 最大思考时间
    "show_ai_reasoning": True,      # 显示AI推理
    "llm_model_type": "fast"        # 默认模型类型
}
```

## 💡 使用建议

### 成本控制
- 使用 `gpt-4o-mini` 或 `deepseek-chat` 降低成本
- 限制游戏局数
- 监控API使用量

### 最佳体验
- **新手**: 使用算法AI (简单/中等难度)
- **进阶**: 使用 LLM AI (OpenAI gpt-4o-mini)
- **高手**: 使用 LLM AI (Claude-3 或 gpt-4o)

### 故障排除
- **网络错误**: 检查网络连接和API地址
- **认证失败**: 验证API密钥是否正确
- **配额超限**: 检查账户余额和使用限制
- **响应超时**: 调整 `max_thinking_time` 参数

## 📊 成本估算

基于每局游戏大约50-100个API调用：

| 提供商 | 模型 | 每局成本 | 月度100局 |
|--------|------|----------|-----------|
| DeepSeek | deepseek-chat | $0.0001 | $0.01 |
| OpenAI | gpt-4o-mini | $0.001 | $0.10 |
| Moonshot | moonshot-v1-8k | $0.002 | $0.20 |
| OpenAI | gpt-4o | $0.01 | $1.00 |
| Anthropic | claude-3-sonnet | $0.005 | $0.50 |

## ⚠️ 注意事项

1. **API密钥安全**: 不要将密钥提交到代码仓库
2. **网络延迟**: LLM AI需要稳定的网络连接
3. **成本控制**: 监控API使用量，避免意外费用
4. **降级机制**: 项目内置算法AI作为故障备用

## 🆘 技术支持

如果遇到问题：
1. 检查API密钥配置
2. 验证网络连接
3. 查看错误日志
4. 尝试降级到算法AI

项目会自动处理大部分错误情况，确保游戏正常进行。