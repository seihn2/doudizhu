# AI斗地主项目架构详解

## 🎯 项目概述

这是一个**本地单人版**AI斗地主游戏，使用纯Python实现，采用**算法AI**而非大语言模型API。

## 🏗️ 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    用户界面层 (UI Layer)                      │
├─────────────────────────────────────────────────────────────┤
│                  游戏控制层 (Game Control)                    │
├─────────────────────────────────────────────────────────────┤
│                  游戏逻辑层 (Game Logic)                      │
├─────────────────────────────────────────────────────────────┤
│                   AI决策层 (AI Layer)                        │
├─────────────────────────────────────────────────────────────┤
│                  基础数据层 (Data Layer)                      │
└─────────────────────────────────────────────────────────────┘
```

## 📁 模块详细说明

### 1. 用户界面层 (ui/)

**ui/console_ui.py** - 主界面控制器
- 负责游戏的整体流程控制
- 处理用户输入和界面显示
- 提供菜单系统、设置管理等

**ui/utils.py** - 界面工具函数
- 颜色输出、表格显示
- 卡牌格式化显示
- 用户输入验证等工具函数

```python
# 示例：界面显示功能
def print_hand_cards(cards: List[Card], title: str = "你的手牌"):
    print(f"\\n{Colors.BRIGHT}{title}:{Colors.RESET}")
    print(f"  {format_card_display(cards)}")
```

### 2. 游戏控制层 (game/game_state.py)

**GameController** - 游戏主控制器
- 管理游戏整体流程
- 控制回合切换
- 处理游戏状态变化

**GameState** - 游戏状态管理
- 存储当前游戏状态
- 记录游戏历史
- 管理玩家信息

```python
class GameController:
    def __init__(self):
        self.state = GameState()
        self.deck = Deck()

    def play_turn(self) -> bool:
        # 执行一个回合的逻辑
        current_player = self.state.get_current_player()
        cards_to_play = current_player.choose_cards_to_play(...)
```

### 3. 游戏逻辑层 (game/)

**game/cards.py** - 卡牌系统
- 定义卡牌类和牌堆类
- 实现洗牌、发牌功能
- 提供手牌管理

**game/rules.py** - 规则引擎
- 牌型识别和验证
- 牌型大小比较
- 出牌合法性检查

**game/player.py** - 玩家基类
- 定义玩家接口
- 实现基础玩家行为

```python
class RuleEngine:
    @staticmethod
    def analyze_cards(cards: List[Card]) -> CardPattern:
        # 分析牌型：单张、对子、三张、顺子等

    @staticmethod
    def can_follow(current_cards: List[Card], last_pattern: CardPattern) -> bool:
        # 检查是否可以跟上一手牌
```

### 4. AI决策层 (ai/)

**ai/ai_player.py** - AI玩家实现
- 继承Player基类
- 集成AI策略
- 模拟人类思考时间

**ai/strategy.py** - AI策略核心
- 不同难度的决策算法
- 叫地主策略
- 出牌策略选择

**ai/card_analyzer.py** - 牌型分析器
- 手牌结构分析
- 牌型组合评估
- 获胜概率计算

```python
class AIStrategy:
    def choose_cards_to_play(self, hand_cards, last_pattern, game_state):
        if last_pattern is None:
            return self._choose_active_play(hand_cards, game_state)
        else:
            return self._choose_follow_play(hand_cards, last_pattern, game_state)
```

## 🤖 AI实现机制

### 当前AI类型：算法AI

**特点：**
- ✅ 基于规则和启发式算法
- ✅ 快速响应（毫秒级）
- ✅ 完全本地运行
- ✅ 无网络依赖

### AI决策流程

```
输入：手牌 + 游戏状态 + 上一手牌
    ↓
1. 牌型结构分析
    ↓
2. 策略选择（根据难度）
    ↓
3. 候选方案生成
    ↓
4. 方案评估和筛选
    ↓
输出：最优出牌决策
```

### AI难度实现

**简单难度：**
- 随机性较强
- 基础出牌策略
- 50%概率跟牌

**中等难度：**
- 平衡的策略选择
- 考虑牌型组合
- 适度的风险控制

**困难难度：**
- 复杂的博弈分析
- 记忆对手出牌
- 高级策略组合

## 🔌 如何接入大语言模型API

如果你想要接入GPT、Claude等大语言模型，可以按以下方式扩展：

### 1. 创建LLM AI玩家

```python
# ai/llm_player.py
class LLMPlayer(Player):
    def __init__(self, name: str, player_id: int, api_config: dict):
        super().__init__(name, player_id)
        self.api_client = self._setup_api_client(api_config)

    def choose_cards_to_play(self, last_pattern, game_state):
        # 构建提示词
        prompt = self._build_prompt(game_state, last_pattern)

        # 调用API
        response = self.api_client.chat_completion(prompt)

        # 解析响应
        return self._parse_ai_response(response)
```

### 2. API配置示例

```python
# config.py
LLM_CONFIG = {
    "provider": "openai",  # 或 "anthropic", "deepseek"
    "api_key": "your-api-key",
    "model": "gpt-4o-mini",
    "base_url": "https://api.openai.com/v1",
    "max_tokens": 1000,
    "temperature": 0.7
}
```

### 3. 提示词工程

```python
def _build_prompt(self, game_state, last_pattern):
    prompt = f'''你是一个专业的斗地主AI玩家。

## 当前游戏状态
- 你的手牌：{self.format_hand_cards()}
- 你的角色：{"地主" if self.is_landlord else "农民"}
- 其他玩家手牌数：{game_state["players_card_count"]}

## 上一手牌
{self.format_last_pattern(last_pattern) if last_pattern else "无人出牌，你可以主动出牌"}

## 请选择出牌
请分析局势并选择最优出牌策略，以JSON格式返回：
{{
    "action": "play_cards" | "pass",
    "cards": [3, 4, 5],  // 牌值数组
    "reasoning": "出牌理由"
}}'''
    return prompt
```

## 🚀 扩展建议

### 1. 混合AI模式
- 结合算法AI和LLM AI
- 根据游戏阶段选择不同AI类型
- 提供更丰富的游戏体验

### 2. AI训练数据收集
- 记录人类玩家的游戏数据
- 分析最优策略
- 用于改进AI算法

### 3. 多模型支持
- 支持多个LLM提供商
- 实现模型降级和故障转移
- 成本控制和优化

## 📊 性能特点

| 特性 | 算法AI | LLM AI |
|------|--------|--------|
| 响应速度 | 毫秒级 | 1-5秒 |
| 运行成本 | 免费 | API费用 |
| 网络依赖 | 无 | 需要 |
| 策略复杂度 | 中等 | 很高 |
| 可解释性 | 高 | 中等 |
| 个性化 | 低 | 很高 |

## 🎮 游戏体验

当前的算法AI已经能够提供：
- 合理的叫地主决策
- 智能的出牌选择
- 不同难度的挑战性
- 流畅的游戏体验

如果你需要接入大语言模型API，我可以帮你实现具体的代码。你更倾向于哪种AI实现方式？