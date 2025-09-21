"""
AI玩家实现模块
整合AI策略，实现完整的AI玩家
"""

import time
import random
from typing import List, Optional, Dict, Any
from game.player import Player
from game.cards import Card
from game.rules import CardPattern
from .strategy import AIStrategy, Difficulty


class AIPlayer(Player):
    """AI玩家类"""

    def __init__(self, name: str, player_id: int, difficulty: Difficulty = Difficulty.MEDIUM):
        """初始化AI玩家"""
        super().__init__(name, player_id)
        self.difficulty = difficulty
        self.strategy = AIStrategy(difficulty)
        self.thinking_time = self._get_thinking_time()
        self.personality = self._generate_personality()

    def _get_thinking_time(self) -> float:
        """获取思考时间（模拟真实玩家）"""
        base_times = {
            Difficulty.EASY: (0.5, 1.5),
            Difficulty.MEDIUM: (1.0, 2.5),
            Difficulty.HARD: (2.0, 4.0)
        }
        min_time, max_time = base_times[self.difficulty]
        return random.uniform(min_time, max_time)

    def _generate_personality(self) -> Dict[str, float]:
        """生成AI个性参数"""
        personalities = {
            Difficulty.EASY: {
                "aggressiveness": random.uniform(0.3, 0.7),
                "caution": random.uniform(0.2, 0.6),
                "cooperation": random.uniform(0.4, 0.8)
            },
            Difficulty.MEDIUM: {
                "aggressiveness": random.uniform(0.4, 0.8),
                "caution": random.uniform(0.3, 0.7),
                "cooperation": random.uniform(0.5, 0.9)
            },
            Difficulty.HARD: {
                "aggressiveness": random.uniform(0.6, 0.9),
                "caution": random.uniform(0.5, 0.8),
                "cooperation": random.uniform(0.7, 1.0)
            }
        }
        return personalities[self.difficulty]

    def decide_landlord(self, bottom_cards: List[Card]) -> bool:
        """决定是否要当地主"""
        print(f"\n{self.name} 正在考虑是否叫地主...")

        # 模拟思考时间
        time.sleep(self.thinking_time * 0.5)

        decision = self.strategy.decide_landlord(self.hand.cards, bottom_cards)

        if decision:
            print(f"{self.name}: 我要当地主！")
        else:
            print(f"{self.name}: 不叫")

        return decision

    def choose_cards_to_play(self, last_pattern: Optional[CardPattern],
                           game_state: Dict[str, Any]) -> Optional[List[Card]]:
        """选择要出的牌"""
        print(f"\n轮到 {self.name} 出牌...")

        # 显示思考过程
        if self.difficulty != Difficulty.EASY:
            self._show_thinking_process(last_pattern, game_state)

        # 模拟思考时间
        think_time = self.thinking_time
        if last_pattern is None:
            think_time *= 1.5  # 主动出牌需要更多思考时间

        time.sleep(think_time)

        # 做出决策
        cards_to_play = self.strategy.choose_cards_to_play(
            self.hand.cards, last_pattern, game_state
        )

        # 显示AI的决策
        if cards_to_play is None:
            print(f"{self.name}: 过")
            return None
        else:
            from game.rules import RuleEngine
            pattern = RuleEngine.analyze_cards(cards_to_play)
            type_name = RuleEngine.get_card_type_name(pattern.card_type)
            cards_str = " ".join(str(card) for card in cards_to_play)
            print(f"{self.name}: {type_name} - {cards_str}")

            # 添加一些个性化的话语
            if self.difficulty != Difficulty.EASY:
                self._add_personality_comment(pattern, cards_to_play, game_state)

            return cards_to_play

    def _show_thinking_process(self, last_pattern: Optional[CardPattern],
                             game_state: Dict[str, Any]):
        """显示AI思考过程"""
        thinking_messages = []

        if last_pattern is None:
            thinking_messages = [
                "分析手牌结构...",
                "寻找最佳出牌组合...",
                "评估风险和收益..."
            ]
        else:
            thinking_messages = [
                "分析上家出牌...",
                "检查可跟牌型...",
                "评估跟牌价值..."
            ]

        if self.difficulty == Difficulty.HARD:
            thinking_messages.extend([
                "分析对手剩余牌型...",
                "计算获胜概率...",
                "制定最优策略..."
            ])

        for msg in thinking_messages:
            print(f"{self.name}: {msg}")
            time.sleep(0.3)

    def _add_personality_comment(self, pattern: CardPattern,
                               cards: List[Card], game_state: Dict[str, Any]):
        """添加个性化评论"""
        comments = []

        # 根据牌型添加评论
        if pattern.card_type.value == "bomb":
            comments = ["炸弹！", "爆炸！", "来个炸弹！"]
        elif pattern.card_type.value == "rocket":
            comments = ["王炸！", "双王！", "最大的！"]
        elif pattern.card_type.value == "straight":
            comments = ["顺子！", "一条龙！", "连起来了！"]
        elif len(cards) == 1 and cards[0].value >= 14:
            comments = ["大牌！", "高手出手！", "压制一下！"]

        # 根据游戏状态添加评论
        players_cards = game_state.get("players_card_count", [])
        if players_cards and min(players_cards) <= 3:
            comments.extend(["要结束了！", "最后冲刺！", "决战时刻！"])

        # 根据AI个性调整评论概率
        if self.personality["aggressiveness"] > 0.7 and random.random() < 0.3:
            if comments:
                print(f"{self.name}: {random.choice(comments)}")

    def get_ai_info(self) -> Dict[str, Any]:
        """获取AI信息（调试用）"""
        return {
            "name": self.name,
            "difficulty": self.difficulty.value,
            "personality": self.personality,
            "hand_count": len(self.hand.cards),
            "is_landlord": self.is_landlord
        }

    def adjust_difficulty(self, new_difficulty: Difficulty):
        """调整AI难度"""
        self.difficulty = new_difficulty
        self.strategy = AIStrategy(new_difficulty)
        self.thinking_time = self._get_thinking_time()
        self.personality = self._generate_personality()
        print(f"{self.name} 的难度已调整为 {new_difficulty.value}")

    def __str__(self) -> str:
        """返回AI玩家信息"""
        base_info = super().__str__()
        return f"{base_info} [AI-{self.difficulty.value}]"


class AIPlayerFactory:
    """AI玩家工厂类"""

    @staticmethod
    def create_ai_player(name: str, player_id: int,
                        difficulty: Difficulty = Difficulty.MEDIUM) -> AIPlayer:
        """创建AI玩家"""
        return AIPlayer(name, player_id, difficulty)

    @staticmethod
    def create_ai_team(difficulty: Difficulty = Difficulty.MEDIUM) -> List[AIPlayer]:
        """创建AI队伍（两个AI对手）"""
        ai_names = [
            "小明", "小红", "小李", "小王", "小张",
            "AI助手", "电脑玩家", "智能对手", "机器人"
        ]

        selected_names = random.sample(ai_names, 2)
        return [
            AIPlayerFactory.create_ai_player(selected_names[0], 1, difficulty),
            AIPlayerFactory.create_ai_player(selected_names[1], 2, difficulty)
        ]

    @staticmethod
    def create_mixed_difficulty_team() -> List[AIPlayer]:
        """创建不同难度的AI队伍"""
        difficulties = [Difficulty.MEDIUM, Difficulty.HARD]
        ai_names = ["聪明的小明", "高手小红"]

        return [
            AIPlayerFactory.create_ai_player(ai_names[0], 1, difficulties[0]),
            AIPlayerFactory.create_ai_player(ai_names[1], 2, difficulties[1])
        ]


if __name__ == "__main__":
    # 测试代码
    from game.cards import Deck

    # 创建AI玩家
    ai1 = AIPlayerFactory.create_ai_player("AI玩家1", 1, Difficulty.MEDIUM)
    ai2 = AIPlayerFactory.create_ai_player("AI玩家2", 2, Difficulty.HARD)

    print(f"创建了AI玩家: {ai1}")
    print(f"创建了AI玩家: {ai2}")

    # 测试发牌
    deck = Deck()
    deck.shuffle()
    p1_cards, p2_cards, _, bottom = deck.deal_cards()

    ai1.receive_cards(p1_cards)
    ai2.receive_cards(p2_cards)

    print(f"\n{ai1.name} 手牌数: {len(ai1.hand.cards)}")
    print(f"{ai2.name} 手牌数: {len(ai2.hand.cards)}")

    # 测试叫地主
    print(f"\n{ai1.name} 叫地主结果: {ai1.decide_landlord(bottom)}")
    print(f"{ai2.name} 叫地主结果: {ai2.decide_landlord(bottom)}")

    # 测试AI信息
    print(f"\nAI1信息: {ai1.get_ai_info()}")
    print(f"AI2信息: {ai2.get_ai_info()}")