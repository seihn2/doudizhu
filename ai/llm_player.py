"""
大语言模型AI玩家实现
支持接入GPT、Claude等大语言模型API
"""

import json
import time
import asyncio
import aiohttp
from typing import List, Optional, Dict, Any
from game.player import Player
from game.cards import Card
from game.rules import CardPattern, RuleEngine


class LLMConfig:
    """LLM配置类"""

    def __init__(self, provider: str, api_key: str, model: str,
                 base_url: str = None, max_tokens: int = 1000, temperature: float = 0.7):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.base_url = base_url or self._get_default_url(provider)
        self.max_tokens = max_tokens
        self.temperature = temperature

    def _get_default_url(self, provider: str) -> str:
        """获取默认API地址"""
        urls = {
            "openai": "https://api.openai.com/v1",
            "anthropic": "https://api.anthropic.com",
            "deepseek": "https://api.deepseek.com",
            "moonshot": "https://api.moonshot.cn/v1"
        }
        return urls.get(provider, "")


class LLMAPIClient:
    """LLM API客户端"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def chat_completion(self, prompt: str) -> str:
        """调用聊天完成API"""
        if self.config.provider == "openai":
            return await self._openai_completion(prompt)
        elif self.config.provider == "anthropic":
            return await self._anthropic_completion(prompt)
        elif self.config.provider == "deepseek":
            return await self._deepseek_completion(prompt)
        else:
            raise ValueError(f"不支持的提供商: {self.config.provider}")

    async def _openai_completion(self, prompt: str) -> str:
        """OpenAI API调用"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": "你是一个专业的斗地主AI玩家，擅长分析局势和制定策略。"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }

        async with self.session.post(
            f"{self.config.base_url}/chat/completions",
            headers=headers,
            json=data
        ) as response:
            result = await response.json()
            return result["choices"][0]["message"]["content"]

    async def _anthropic_completion(self, prompt: str) -> str:
        """Claude API调用"""
        headers = {
            "x-api-key": self.config.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        data = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        async with self.session.post(
            f"{self.config.base_url}/messages",
            headers=headers,
            json=data
        ) as response:
            result = await response.json()
            return result["content"][0]["text"]

    async def _deepseek_completion(self, prompt: str) -> str:
        """DeepSeek API调用"""
        # DeepSeek使用类似OpenAI的接口
        return await self._openai_completion(prompt)


class LLMPlayer(Player):
    """大语言模型AI玩家"""

    def __init__(self, name: str, player_id: int, config: LLMConfig):
        super().__init__(name, player_id)
        self.config = config
        self.api_client = None
        self.thinking_time = 2.0  # LLM需要更长思考时间

    def decide_landlord(self, bottom_cards: List[Card]) -> bool:
        """决定是否要当地主"""
        print(f"\n{self.name} 正在通过AI分析是否叫地主...")

        # 构建提示词
        prompt = self._build_landlord_prompt(bottom_cards)

        # 调用LLM
        try:
            response = asyncio.run(self._call_llm(prompt))
            decision = self._parse_landlord_response(response)

            if decision:
                print(f"{self.name}: 我要当地主！")
            else:
                print(f"{self.name}: 不叫")

            return decision

        except Exception as e:
            print(f"{self.name}: AI调用失败，使用默认策略 ({e})")
            # 降级到简单策略
            return len([c for c in self.hand.cards + bottom_cards if c.value >= 14]) >= 3

    def choose_cards_to_play(self, last_pattern: Optional[CardPattern],
                           game_state: Dict[str, Any]) -> Optional[List[Card]]:
        """选择要出的牌"""
        print(f"\n{self.name} 正在通过AI分析最佳出牌...")

        # 显示思考过程
        time.sleep(self.thinking_time)

        # 构建提示词
        prompt = self._build_play_prompt(last_pattern, game_state)

        try:
            response = asyncio.run(self._call_llm(prompt))
            cards_to_play = self._parse_play_response(response)

            if cards_to_play is None:
                print(f"{self.name}: 过")
                return None
            else:
                pattern = RuleEngine.analyze_cards(cards_to_play)
                type_name = RuleEngine.get_card_type_name(pattern.card_type)
                cards_str = " ".join(str(card) for card in cards_to_play)
                print(f"{self.name}: {type_name} - {cards_str}")
                return cards_to_play

        except Exception as e:
            print(f"{self.name}: AI调用失败，使用备用策略 ({e})")
            # 降级到算法AI
            return self._fallback_strategy(last_pattern, game_state)

    async def _call_llm(self, prompt: str) -> str:
        """调用LLM API"""
        async with LLMAPIClient(self.config) as client:
            return await client.chat_completion(prompt)

    def _build_landlord_prompt(self, bottom_cards: List[Card]) -> str:
        """构建叫地主提示词"""
        hand_values = [card.value for card in self.hand.cards]
        bottom_values = [card.value for card in bottom_cards]

        prompt = f"""你是一个顶级斗地主高手，以激进和精准的策略著称！现在需要决定是否叫地主。

## 你的手牌
牌值：{hand_values}
牌数：{len(self.hand.cards)}张

## 底牌
牌值：{bottom_values}

## 牌值说明
- 3-10: 普通牌
- 11: J, 12: Q, 13: K, 14: A, 15: 2
- 16: 小王, 17: 大王

## 高手策略原则
1. **激进叫地主**: 有一定胜算就敢于挑战，不要过于保守
2. **大牌控制**: 重视A、2、王的控制力，即使数量不多也要敢拼
3. **牌型潜力**: 关注顺子、连对、飞机等高效牌型的可能性
4. **底牌加成**: 底牌可能大幅改善手牌结构，要积极考虑
5. **心理博弈**: 适当的冒险精神是高手必备

## 叫地主标准
- 有王炸或大炸弹: 90%叫地主
- 有小王或大王: 70%叫地主
- 有多个A或2: 60%叫地主
- 有良好牌型组合: 50%叫地主
- 底牌有潜力改善: 增加20%概率

请以JSON格式返回决策：
{{
    "decision": true/false,
    "confidence": 0.85,
    "reasoning": "作为高手的决策理由，要体现激进和自信"
}}"""
        return prompt

    def _build_play_prompt(self, last_pattern: Optional[CardPattern],
                          game_state: Dict[str, Any]) -> str:
        """构建出牌提示词"""
        hand_values = [card.value for card in self.hand.cards]

        # 构建游戏状态信息
        state_info = f"""
## 当前游戏状态
- 你的手牌：{hand_values} (共{len(self.hand.cards)}张)
- 你的角色：{"地主" if self.is_landlord else "农民"}
- 其他玩家手牌数：{game_state.get('players_card_count', [])}
- 当前回合：{game_state.get('round_count', 0)}
"""

        # 上一手牌信息
        last_play_info = ""
        if last_pattern:
            last_cards = [card.value for card in last_pattern.cards]
            type_name = RuleEngine.get_card_type_name(last_pattern.card_type)
            last_play_info = f"""
## 上一手牌
- 牌型：{type_name}
- 牌值：{last_cards}
- 出牌玩家：玩家{game_state.get('last_player_idx', '未知')}
"""
        else:
            last_play_info = "\n## 上一手牌\n无人出牌，你可以主动出牌"

        # 分析对手威胁等级
        threat_level = "低"
        if game_state:
            players_card_count = game_state.get('players_card_count', [])
            current_idx = game_state.get('current_player_idx', 0)
            opponent_cards = [count for i, count in enumerate(players_card_count) if i != current_idx]
            if opponent_cards and min(opponent_cards) <= 5:
                threat_level = "高"
            elif opponent_cards and min(opponent_cards) <= 10:
                threat_level = "中"

        prompt = f"""你是一个世界级斗地主大师，以咄咄逼人的攻击性风格和精准的战术闻名！

{state_info}
{last_play_info}

## 当前威胁等级: {threat_level}

## 牌型规则和威力评估
- 单张、对子: 基础牌型，优先出小牌
- 三张、三带一、三带对: 中等威力，可主动进攻
- 顺子(5+张连续): 高威力，一次出多张，优先考虑
- 连对(3+对连续): 高威力，压制效果强
- 飞机: 超高威力，震慑对手
- 炸弹: 终极武器，控制全局
- 王炸: 绝对统治力

## 大师级策略原则
1. **主动攻击**: 能出大牌就出大牌，不要犹豫！
2. **节奏控制**: 出牌要有节奏感，压制对手
3. **威胁感知**: 对手牌少时必须强力压制
4. **组合优先**: 优先出顺子、连对等高效牌型
5. **心理战**: 展现强势，让对手产生压力

## 出牌决策准则
- 威胁等级高: 优先出大牌压制，不惜代价
- 威胁等级中: 积极出牌，保持压力
- 威胁等级低: 优化手牌结构，为后续做准备
- 有炸弹时: 该出手时就出手，不要保守
- 手牌少时: 全力冲刺，争取一举获胜

## 禁止过度保守
- 不要轻易过牌，除非确实无法跟牌
- 不要过分保留大牌，适时施压才是王道
- 不要被对手的小打小闹迷惑，保持攻击性

请以JSON格式返回决策：
{{
    "action": "play_cards" | "pass",
    "cards": [3, 4, 5],
    "reasoning": "展现大师风范的决策理由，要体现攻击性和自信",
    "confidence": 0.85
}}"""
        return prompt

    def _parse_landlord_response(self, response: str) -> bool:
        """解析叫地主响应"""
        try:
            # 尝试提取JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
                return data.get('decision', False)
        except:
            pass

        # 备用解析：关键词匹配
        response_lower = response.lower()
        if any(word in response_lower for word in ['叫地主', 'true', '要', '是']):
            return True
        return False

    def _parse_play_response(self, response: str) -> Optional[List[Card]]:
        """解析出牌响应"""
        try:
            # 尝试提取JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)

                if data.get('action') == 'pass':
                    return None

                card_values = data.get('cards', [])
                if card_values:
                    return self._values_to_cards(card_values)
        except:
            pass

        # 解析失败，返回None（过牌）
        return None

    def _values_to_cards(self, values: List[int]) -> List[Card]:
        """将牌值转换为Card对象"""
        result_cards = []
        available_cards = self.hand.cards.copy()

        for value in values:
            for card in available_cards:
                if card.value == value and card not in result_cards:
                    result_cards.append(card)
                    break

        return result_cards

    def _fallback_strategy(self, last_pattern: Optional[CardPattern],
                          game_state: Dict[str, Any]) -> Optional[List[Card]]:
        """备用策略（算法AI）"""
        # 这里可以调用原来的算法AI作为备用
        from .strategy import AIStrategy, Difficulty
        fallback_ai = AIStrategy(Difficulty.MEDIUM)
        return fallback_ai.choose_cards_to_play(self.hand.cards, last_pattern, game_state)


# 工厂函数
def create_llm_player(name: str, player_id: int, provider: str,
                     api_key: str, model: str = None) -> LLMPlayer:
    """创建LLM AI玩家"""

    # 默认模型配置
    default_models = {
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-haiku-20240307",
        "deepseek": "deepseek-chat",
        "moonshot": "moonshot-v1-8k"
    }

    if not model:
        model = default_models.get(provider, "gpt-3.5-turbo")

    config = LLMConfig(
        provider=provider,
        api_key=api_key,
        model=model,
        max_tokens=1000,
        temperature=0.7
    )

    return LLMPlayer(name, player_id, config)


if __name__ == "__main__":
    # 使用示例
    config = LLMConfig(
        provider="openai",
        api_key="your-api-key-here",
        model="gpt-4o-mini"
    )

    player = LLMPlayer("GPT玩家", 1, config)
    print(f"创建了LLM AI玩家: {player.name}")