# 硅基流动模型选择使用指南

## 概述

斗地主游戏现在支持硅基流动的多种AI模型选择，提供了从快速经济到高质量推理的多种选项。

## 功能特点

### 支持的模型分类

1. **推荐模型** - 适合大多数用户的平衡选择
   - Qwen2.5-7B (快速、经济)
   - DeepSeek-V2.5 (智能推理)
   - Claude-3.5-Sonnet (高质量)
   - GPT-4o-mini (均衡)

2. **Qwen系列** - 阿里云通义千问模型
   - Qwen2.5-7B / 14B / 32B / 72B

3. **DeepSeek系列** - 深度求索模型
   - DeepSeek-V2.5 (通用推理)
   - DeepSeek-Coder-V2 (代码专精)

4. **Claude系列** - Anthropic模型
   - Claude-3.5-Sonnet (高质量)
   - Claude-3.5-Haiku (快速)

5. **GPT系列** - OpenAI模型
   - GPT-4o
   - GPT-4o-mini

6. **其他模型** - 更多选择
   - Yi-Lightning / Yi-Large
   - ChatGLM3-6B
   - Llama3.1 (8B/70B/405B)
   - InternLM2.5 (7B/20B)

## 使用方法

### 1. 设置API密钥

```bash
# 设置环境变量
export SILICONFLOW_API_KEY=your_api_key_here

# 或在Windows中
set SILICONFLOW_API_KEY=your_api_key_here
```

### 2. 启动游戏

```bash
python main_with_llm.py
```

### 3. 选择AI类型

1. 在主菜单中选择 "AI类型设置"
2. 选择 "使用LLM AI（在线，智能）"
3. 选择 "siliconflow" 作为提供商

### 4. 选择模型

选择硅基流动后，会进入模型选择界面：

1. **选择模型分类**
   - 推荐模型 (适合新手)
   - 按系列选择 (Qwen/DeepSeek/Claude/GPT)
   - 其他模型 (更多选择)

2. **选择具体模型**
   - 每个分类下显示可用模型
   - 包含模型描述和特点说明

3. **确认选择**
   - 系统会显示选择的模型信息
   - 游戏中会使用该模型进行AI决策

## 模型推荐

### 快速游戏
- **Qwen2.5-7B**: 响应快，成本低，适合日常游戏
- **GPT-4o-mini**: 均衡性能，稳定可靠

### 高质量体验
- **Claude-3.5-Sonnet**: 推理质量高，策略智能
- **DeepSeek-V2.5**: 专业级推理能力

### 特殊需求
- **DeepSeek-Coder-V2**: 如果需要更逻辑化的推理
- **Llama3.1-70B**: 大模型，推理能力强

## 配置保存

选择的模型配置会自动保存，下次启动游戏时会保持之前的选择。

当前配置会在"AI类型设置"中显示，例如：
- `当前配置: 硅基流动 - Qwen2.5-7B (快速、经济)`

## 故障排除

### 1. 看不到硅基流动选项
- 检查是否设置了 `SILICONFLOW_API_KEY`
- 确认API密钥长度正确（通常较长）

### 2. 模型选择界面空白
- 检查配置文件中的 `model_categories` 是否存在
- 重新启动游戏

### 3. 游戏中AI无响应
- 检查网络连接
- 验证API密钥是否有效
- 查看控制台错误信息

### 4. 降级到算法AI
- 如果LLM调用失败，游戏会自动降级使用本地算法AI
- 检查API密钥和网络连接后重新选择

## 成本考虑

不同模型的调用成本不同：

**经济型**:
- Qwen2.5-7B
- ChatGLM3-6B

**标准型**:
- DeepSeek-V2.5
- GPT-4o-mini

**高级型**:
- Claude-3.5-Sonnet
- GPT-4o
- Llama3.1-70B

## 技术细节

### 配置文件
- 模型配置位于 `config.py` 的 `siliconflow` 部分
- 支持动态添加新模型

### API调用
- 使用OpenAI兼容的接口格式
- 支持异步调用和错误重试
- 自动降级机制保证游戏稳定性

### 菜单系统
- 分类式模型选择界面
- 显示模型描述和特点
- 保存用户选择偏好

现在你可以在斗地主游戏中体验各种顶级AI模型的不同策略风格！