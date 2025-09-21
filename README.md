# AI斗地主 - 本地单人版

基于Python的AI斗地主游戏，支持本地单人模式，玩家与两个AI对手进行经典斗地主对战。

## 项目特色

- 🎮 经典斗地主规则实现
- 🤖 智能AI对手
- 💻 本地运行，无需网络
- 🎯 简洁易用的命令行界面
- ⚡ 快速响应的游戏体验

## 技术架构

### 目录结构
```
doudizhu/
├── main.py                 # 游戏入口
├── requirements.txt        # 依赖包
├── game/                   # 游戏核心模块
│   ├── __init__.py
│   ├── cards.py           # 卡牌系统
│   ├── rules.py           # 游戏规则
│   ├── game_state.py      # 游戏状态管理
│   └── player.py          # 玩家基类
├── ai/                     # AI模块
│   ├── __init__.py
│   ├── ai_player.py       # AI玩家实现
│   ├── strategy.py        # AI策略
│   └── card_analyzer.py   # 牌型分析
├── ui/                     # 用户界面
│   ├── __init__.py
│   ├── console_ui.py      # 控制台界面
│   └── utils.py           # UI工具函数
└── tests/                  # 测试文件
    ├── __init__.py
    ├── test_cards.py
    ├── test_rules.py
    └── test_ai.py
```

### 核心模块说明

1. **卡牌系统 (cards.py)**: 实现54张扑克牌的表示、洗牌、发牌等功能
2. **游戏规则 (rules.py)**: 实现斗地主的牌型识别、大小比较、出牌验证等核心规则
3. **游戏状态 (game_state.py)**: 管理游戏的当前状态，包括玩家手牌、当前轮次、历史出牌等
4. **AI玩家 (ai_player.py)**: 实现AI的决策逻辑，包括叫地主、出牌等策略
5. **用户界面 (console_ui.py)**: 提供简洁的命令行交互界面

## 游戏特性

### 支持的牌型
- 单牌、对子、三张
- 三带一、三带对
- 顺子、连对、飞机
- 炸弹、王炸

### AI难度等级
- 简单: 基础策略，随机性较强
- 中等: 平衡策略，考虑牌型组合
- 困难: 高级策略，记牌和推理

### 游戏模式
- 单局模式: 完成一局游戏
- 连续模式: 多局游戏，统计胜负

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动游戏

#### 🚀 推荐方式（自动检测）
```bash
python start_game.py
```

#### 🎮 手动选择版本
```bash
# 基础版（算法AI + 出牌推荐）
python main.py

# 增强版（LLM AI + 出牌推荐，需要API密钥）
python main_with_llm.py
```

### 3. LLM AI设置（可选）

如果想体验更智能的AI对手，可以设置API密钥：

```bash
# Windows
set DEEPSEEK_API_KEY=sk-your-deepseek-key-here

# Linux/Mac
export DEEPSEEK_API_KEY=sk-your-deepseek-key-here
```

支持的LLM提供商：
- **DeepSeek** (推荐，性价比高)
- OpenAI GPT
- Anthropic Claude
- Moonshot AI

### 4. 游戏特色

✨ **最新增强功能**：
- 🛡️ **智能错误防护** - 无效牌型自动拦截
- 🤖 **出牌推荐系统** - AI级别的策略建议
- 🔥 **激进AI对手** - 更具挑战性的游戏体验
- ⚙️ **灵活配置** - 可自定义各种游戏设置