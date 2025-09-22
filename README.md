# AI斗地主游戏

一个基于Python后端和React前端的在线斗地主游戏，支持与AI对手对战。同时保留了原版控制台游戏。

## 功能特色

- 🎮 **完整的斗地主游戏逻辑** - 支持标准斗地主规则
- 🤖 **智能AI对手** - 基于策略算法的AI玩家
- 🌐 **实时多人对战** - WebSocket实时通信
- 💻 **现代化界面** - React + Ant Design精美UI
- 📱 **响应式设计** - 支持桌面和移动设备
- 🎯 **原版控制台** - 保留经典命令行版本

## 技术栈

### 后端
- **FastAPI** - 现代、快速的Web框架
- **WebSocket** - 实时双向通信
- **Python** - 游戏逻辑和AI算法

### 前端
- **React 18** - 现代React框架
- **Ant Design** - 企业级UI组件库
- **Zustand** - 轻量级状态管理
- **WebSocket** - 实时通信

## 项目结构

```
doudizhu/
├── backend/                 # FastAPI后端
│   ├── main.py             # 应用入口
│   ├── models/             # 数据模型
│   ├── websocket/          # WebSocket处理
│   └── requirements.txt    # Python依赖
├── frontend/               # React前端
│   ├── src/
│   │   ├── components/     # React组件
│   │   ├── services/       # API服务
│   │   ├── hooks/          # React hooks
│   │   └── store/          # 状态管理
│   └── package.json        # Node.js依赖
├── game/                   # 游戏核心逻辑
│   ├── cards.py           # 卡牌系统
│   ├── rules.py           # 游戏规则
│   ├── game_state.py      # 游戏状态管理
│   └── player.py          # 玩家基类
├── ai/                     # AI系统
│   ├── ai_player.py       # AI玩家
│   ├── strategy.py        # AI策略
│   └── card_analyzer.py   # 牌型分析
└── ui/                     # 控制台界面（原版）
    └── console_ui.py
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

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 安装依赖

**后端依赖:**
```bash
pip install -r backend/requirements.txt
```

**前端依赖:**
```bash
cd frontend
npm install
```

### 启动应用

**1. 启动后端服务:**
```bash
cd backend
python main.py
```
后端服务将在 http://localhost:8000 启动

**2. 启动前端应用:**
```bash
cd frontend
npm start
```
前端应用将在 http://localhost:3000 启动

### 游戏说明

1. **创建/加入房间** - 输入玩家名称，选择快速开始或加入指定房间
2. **等待玩家** - 房间需要3名玩家才能开始游戏
3. **叫地主** - 系统自动分配地主（简化实现）
4. **开始游戏** - 按顺序出牌，遵循斗地主规则
5. **胜利条件** - 最先出完手牌的玩家获胜

## API文档

启动后端服务后，访问 http://localhost:8000/docs 查看自动生成的API文档。

## WebSocket事件

### 客户端发送
- `play_cards` - 出牌
- `pass` - 过牌
- `chat` - 聊天消息

### 服务端推送
- `player_joined` - 玩家加入
- `player_left` - 玩家离开
- `game_state` - 游戏状态更新
- `game_start` - 游戏开始
- `game_end` - 游戏结束
- `chat` - 聊天消息广播

## 开发说明

### 后端开发
- 游戏逻辑在 `game/` 目录中，已经实现完整的斗地主规则
- AI系统在 `ai/` 目录中，支持不同难度的AI策略
- WebSocket处理在 `backend/websocket/` 中

### 前端开发
- 组件开发遵循Ant Design设计规范
- 状态管理使用Zustand，简单易用
- WebSocket连接通过自定义Hook管理

## 原版控制台游戏

项目保留了原始的控制台版本，可以通过以下方式体验：

```bash
python main.py              # 人机对战
python main_with_llm.py     # LLM增强版（需要配置API）
```

### LLM AI设置（控制台版）

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

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交Issue和Pull Request！

---

🎮 享受游戏，与AI一较高下！