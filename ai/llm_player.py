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
            "moonshot": "https://api.moonshot.cn/v1",
            "siliconflow": "https://api.siliconflow.cn/v1"
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
        elif self.config.provider == "siliconflow":
            return await self._siliconflow_completion(prompt)
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

    async def _siliconflow_completion(self, prompt: str) -> str:
        """硅基流动 API调用"""
        # 硅基流动使用类似OpenAI的接口格式
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
            "temperature": self.config.temperature,
            "stream": False
        }

        async with self.session.post(
            f"{self.config.base_url}/chat/completions",
            headers=headers,
            json=data
        ) as response:
            result = await response.json()

            # 检查是否有错误
            if "error" in result:
                raise Exception(f"硅基流动API错误: {result['error']['message']}")

            return result["choices"][0]["message"]["content"]


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

        # 最多重试3次
        max_retries = 3
        error_feedback = ""

        for attempt in range(max_retries):
            try:
                # 构建提示词（包含错误反馈）
                prompt = self._build_play_prompt(last_pattern, game_state, error_feedback)

                response = asyncio.run(self._call_llm(prompt))
                if attempt == 0:  # 只在第一次尝试时显示完整响应
                    print(f"  {self.name}: LLM原始响应: {response[:200]}...")

                cards_to_play = self._parse_play_response(response)

                if cards_to_play is None:
                    print(f"{self.name}: 过")
                    return None

                # 验证出牌是否合法和符合规则
                validation_result = self._validate_play_choice(cards_to_play, last_pattern, game_state)

                if validation_result["valid"]:
                    # 出牌合法，返回结果
                    pattern = RuleEngine.analyze_cards(cards_to_play)
                    type_name = RuleEngine.get_card_type_name(pattern.card_type)
                    cards_str = " ".join(str(card) for card in cards_to_play)
                    print(f"{self.name}: {type_name} - {cards_str}")
                    return cards_to_play
                else:
                    # 出牌不合法，准备重试
                    error_feedback = validation_result["error_message"]
                    print(f"  {self.name}: 第{attempt + 1}次尝试失败 - {error_feedback}")

                    if attempt < max_retries - 1:
                        print(f"  {self.name}: 重新分析中...")
                        time.sleep(0.5)  # 短暂等待

            except Exception as e:
                error_feedback = f"解析响应时发生错误: {str(e)}"
                print(f"  {self.name}: 第{attempt + 1}次尝试出现异常 - {error_feedback}")

        # 所有重试都失败，使用备用策略
        print(f"{self.name}: AI多次尝试失败，使用备用策略")
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
                          game_state: Dict[str, Any], error_feedback: str = "") -> str:
        """构建出牌提示词"""
        hand_values = [card.value for card in self.hand.cards]
        hand_values_sorted = sorted(hand_values)

        # 构建游戏状态信息
        state_info = f"""
## 当前游戏状态
- 你的手牌：{hand_values_sorted} (共{len(self.hand.cards)}张)
- 你的角色：{"地主" if self.is_landlord else "农民"}
- 其他玩家手牌数：{game_state.get('players_card_count', [])}
- 当前回合：{game_state.get('round_count', 0)}
"""

        # 分析当前游戏状态
        current_player_idx = game_state.get('current_player_idx', 0)
        last_player_idx = game_state.get('last_player_idx', None)
        pass_count = game_state.get('pass_count', 0)

        # 上一手牌信息和跟牌要求
        last_play_info = ""
        follow_requirement = ""

        if last_pattern is None:
            # 情况1: 无上一手牌 - 开局或轮次结束后获得主动权
            last_play_info = """
## 当前状态
- 你拥有主动出牌权
- 这是新的一轮开始（开局或上轮结束后）
"""
            follow_requirement = """
## 主动出牌
**你可以自由选择任何合法的牌型组合！**
- 可以出任何有效的牌型：单张、对子、三张、顺子等
- 建议选择最优的牌型组合来控制局面
- 考虑手牌结构，优先出难以搭配的牌
"""
        else:
            # 情况2: 有上一手牌，需要分析是否需要跟牌
            last_cards = [card.value for card in last_pattern.cards]
            type_name = RuleEngine.get_card_type_name(last_pattern.card_type)

            # 关键逻辑：如果上一手牌存在，当前玩家必须跟牌或过牌
            # 只有当连续2人过牌后，系统才会清除last_pattern，进入新轮次
            last_play_info = f"""
## 上一手牌
- 牌型：{type_name}
- 牌值：{last_cards}
- 张数：{len(last_pattern.cards)}张
- 出牌玩家：玩家{last_player_idx}
- 已过牌人数：{pass_count}
"""
            follow_requirement = f"""
## 跟牌要求
**你必须跟上这手牌或选择过牌：**
1. 跟牌条件：
   - 牌型必须与上一手相同（{type_name}）
   - 张数必须相同（{len(last_pattern.cards)}张）
   - 主牌值必须大于{last_pattern.main_value}
   - 或者使用炸弹/王炸压制

2. 过牌条件：
   - 无法满足跟牌条件时必须选择"pass"
   - 过牌后如果连续2人过牌，出牌者将获得下轮主动权

**重要：除非使用炸弹/王炸，否则必须出相同牌型！**
"""

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

        # 错误反馈部分
        error_section = ""
        if error_feedback:
            error_section = f"""
## ⚠️ 上次出牌错误反馈
{error_feedback}

**请仔细分析错误原因，重新选择合法的出牌！**
"""

        prompt = f"""你是一个顶级斗地主AI，必须严格遵守游戏规则！

{state_info}
{last_play_info}
{follow_requirement}
{error_section}

## 当前威胁等级: {threat_level}

## 斗地主牌型规则（必须严格遵守）
### 基础牌型
- **单张**: 1张牌，任意牌值
- **对子**: 2张相同牌值的牌
- **三张**: 3张相同牌值的牌
- **三带一**: 3张相同牌值 + 1张任意牌
- **三带对**: 3张相同牌值 + 1对任意牌

### 连续牌型
- **顺子**: 至少5张连续的单张（3,4,5,6,7）注意：2和王不能参与顺子
- **连对**: 至少3对连续的对子（33,44,55）注意：2和王不能参与连对
- **飞机**: 至少2组连续的三张（333,444）
- **飞机带单**: 飞机 + 相应数量的单张
- **飞机带对**: 飞机 + 相应数量的对子

### 特殊牌型
- **四带二单**: 4张相同牌值 + 2张不同的单张
- **四带二对**: 4张相同牌值 + 2对不同的对子
- **炸弹**: 4张相同牌值的牌
- **王炸**: 小王(16) + 大王(17)

## 牌值说明
- 3,4,5,6,7,8,9,10,11(J),12(Q),13(K),14(A),15(2),16(小王),17(大王)
- 大小顺序：3 < 4 < ... < A < 2 < 小王 < 大王
- 注意：2,小王,大王不能参与顺子和连对

## 出牌验证规则
**必须验证：**
1. 检查所选牌值是否都在你的手牌中
2. 检查所选牌型是否合法
3. 如果是跟牌，检查是否能压过上一手牌
4. 不能出不存在的牌或重复的牌

## 策略原则
1. **规则优先**: 永远不要出不合法的牌！
2. **主动攻击**: 能出大牌就出大牌
3. **威胁感知**: 对手牌少时必须压制
4. **组合优先**: 优先出顺子、连对等高效牌型

请以JSON格式返回决策（必须严格按照格式）：
{{
    "action": "play_cards" | "pass",
    "cards": [3, 4, 5],
    "card_type": "顺子",
    "reasoning": "详细的决策理由，包括规则验证",
    "confidence": 0.85
}}

**重要提醒：**
- 如果是跟牌但无法满足条件，必须返回"pass"
- cards数组中的牌值必须都在你的手牌中
- 确保所选牌型是合法的斗地主牌型"""
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
                    print(f"  {self.name}: AI选择过牌")
                    return None

                card_values = data.get('cards', [])
                if not card_values:
                    print(f"  {self.name}: AI未提供牌值，默认过牌")
                    return None

                # 验证牌值是否合法
                if not self._validate_card_values(card_values):
                    print(f"  {self.name}: AI提供的牌值不合法: {card_values}，过牌")
                    return None

                # 转换为牌对象
                cards_to_play = self._values_to_cards(card_values)
                if not cards_to_play:
                    print(f"  {self.name}: 无法获取指定牌值的牌: {card_values}，过牌")
                    return None

                # 验证牌型是否合法
                if not RuleEngine.is_valid_cards(cards_to_play):
                    print(f"  {self.name}: AI出的牌型不合法: {card_values}，过牌")
                    return None

                print(f"  {self.name}: AI选择出牌: {card_values}")
                return cards_to_play

        except json.JSONDecodeError as e:
            print(f"  {self.name}: JSON解析失败: {e}，过牌")
        except Exception as e:
            print(f"  {self.name}: 响应解析失败: {e}，过牌")

        # 解析失败，返回None（过牌）
        return None

    def _validate_card_values(self, values: List[int]) -> bool:
        """验证牌值是否合法"""
        if not values:
            return False

        # 检查牌值范围
        for value in values:
            if not isinstance(value, int) or value < 3 or value > 17:
                print(f"    无效的牌值: {value}")
                return False

        # 检查是否有重复数量超过手牌的情况
        hand_value_count = {}
        for card in self.hand.cards:
            hand_value_count[card.value] = hand_value_count.get(card.value, 0) + 1

        required_value_count = {}
        for value in values:
            required_value_count[value] = required_value_count.get(value, 0) + 1

        for value, count in required_value_count.items():
            if hand_value_count.get(value, 0) < count:
                print(f"    手牌中{value}的数量不足: 需要{count}张，实际有{hand_value_count.get(value, 0)}张")
                return False

        return True

    def _values_to_cards(self, values: List[int]) -> List[Card]:
        """将牌值转换为Card对象"""
        result_cards = []
        available_cards = self.hand.cards.copy()

        # 统计手牌中每个牌值的数量
        hand_value_count = {}
        for card in available_cards:
            hand_value_count[card.value] = hand_value_count.get(card.value, 0) + 1

        # 统计要出的牌值数量
        required_value_count = {}
        for value in values:
            required_value_count[value] = required_value_count.get(value, 0) + 1

        # 检查是否有足够的牌
        for value, count in required_value_count.items():
            if hand_value_count.get(value, 0) < count:
                print(f"    手牌中{value}的数量不足: 需要{count}张，实际有{hand_value_count.get(value, 0)}张")
                return []

        # 按顺序选择牌
        used_cards = set()
        for value in values:
            found = False
            for i, card in enumerate(available_cards):
                if card.value == value and i not in used_cards:
                    result_cards.append(card)
                    used_cards.add(i)
                    found = True
                    break
            if not found:
                print(f"    找不到牌值{value}的可用牌")
                return []

        return result_cards

    def _validate_play_choice(self, cards_to_play: List[Card],
                            last_pattern: Optional[CardPattern],
                            game_state: Dict[str, Any]) -> Dict[str, Any]:
        """验证出牌选择是否合法"""
        try:
            # 1. 检查牌型是否合法
            pattern = RuleEngine.analyze_cards(cards_to_play)
            if not RuleEngine.is_valid_cards(cards_to_play):
                card_values = [card.value for card in cards_to_play]
                return {
                    "valid": False,
                    "error_message": f"牌型不合法: {card_values}。请检查是否符合斗地主牌型规则。"
                }

            # 2. 检查是否需要跟牌
            if last_pattern is not None:
                # 有上一手牌存在，必须能够跟上或使用炸弹/王炸
                if not RuleEngine.can_follow(cards_to_play, last_pattern):
                    card_values = [card.value for card in cards_to_play]
                    last_cards = [card.value for card in last_pattern.cards]
                    last_type = RuleEngine.get_card_type_name(last_pattern.card_type)
                    current_type = RuleEngine.get_card_type_name(pattern.card_type)

                    # 检查是否是炸弹或王炸（可以压任何牌型）
                    from game.rules import CardType
                    if pattern.card_type not in [CardType.BOMB, CardType.ROCKET]:
                        if pattern.card_type != last_pattern.card_type:
                            return {
                                "valid": False,
                                "error_message": f"牌型不匹配: 上家出的是{last_type}({last_cards})，你出的是{current_type}({card_values})。必须出相同牌型或炸弹/王炸。"
                            }
                        elif len(cards_to_play) != len(last_pattern.cards):
                            return {
                                "valid": False,
                                "error_message": f"张数不匹配: 上家出了{len(last_pattern.cards)}张牌，你出了{len(cards_to_play)}张牌。必须出相同张数的牌。"
                            }
                        elif pattern.main_value <= last_pattern.main_value:
                            return {
                                "valid": False,
                                "error_message": f"牌值太小: 上家的主牌值是{last_pattern.main_value}，你的主牌值是{pattern.main_value}。必须出更大的牌。"
                            }
                        else:
                            return {
                                "valid": False,
                                "error_message": f"无法跟上: {card_values}无法跟上家的{last_cards}。请重新选择或过牌。"
                            }

            # 3. 检查牌是否真的在手牌中
            hand_value_count = {}
            for card in self.hand.cards:
                hand_value_count[card.value] = hand_value_count.get(card.value, 0) + 1

            play_value_count = {}
            for card in cards_to_play:
                play_value_count[card.value] = play_value_count.get(card.value, 0) + 1

            for value, count in play_value_count.items():
                if hand_value_count.get(value, 0) < count:
                    return {
                        "valid": False,
                        "error_message": f"牌值{value}数量不足: 手牌中只有{hand_value_count.get(value, 0)}张，但要出{count}张。"
                    }

            # 所有检查通过
            return {"valid": True, "error_message": ""}

        except Exception as e:
            return {
                "valid": False,
                "error_message": f"验证过程出错: {str(e)}"
            }

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
        "moonshot": "moonshot-v1-8k",
        "siliconflow": "Qwen/Qwen2.5-7B-Instruct"
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