"""
AI策略模块
实现不同难度的AI决策策略
"""

import random
from enum import Enum
from typing import List, Optional, Dict, Any
from game.cards import Card
from game.rules import CardPattern, CardType, RuleEngine
from .card_analyzer import CardAnalyzer


class Difficulty(Enum):
    """AI难度等级"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class AIStrategy:
    """AI策略基类"""

    def __init__(self, difficulty: Difficulty):
        self.difficulty = difficulty
        self.analyzer = CardAnalyzer()

    def decide_landlord(self, hand_cards: List[Card], bottom_cards: List[Card]) -> bool:
        """决定是否要当地主"""
        structure = self.analyzer.analyze_hand_structure(hand_cards + bottom_cards)

        # 基础评分
        score = 0

        # 强牌评分
        if structure["has_rockets"]:
            score += 30
        score += len(structure["bombs"]) * 25
        score += len(structure["triples"]) * 8
        score += len(structure["pairs"]) * 3

        # 根据难度调整阈值
        thresholds = {
            Difficulty.EASY: 20,
            Difficulty.MEDIUM: 30,
            Difficulty.HARD: 35
        }

        threshold = thresholds[self.difficulty]

        # 添加随机性
        if self.difficulty == Difficulty.EASY:
            threshold += random.randint(-10, 10)
        elif self.difficulty == Difficulty.MEDIUM:
            threshold += random.randint(-5, 5)

        return score >= threshold

    def choose_cards_to_play(self, hand_cards: List[Card],
                           last_pattern: Optional[CardPattern],
                           game_state: Dict[str, Any]) -> Optional[List[Card]]:
        """选择要出的牌"""
        if last_pattern is None:
            # 主动出牌
            return self._choose_active_play(hand_cards, game_state)
        else:
            # 跟牌
            return self._choose_follow_play(hand_cards, last_pattern, game_state)

    def _choose_active_play(self, hand_cards: List[Card], game_state: Dict[str, Any]) -> List[Card]:
        """主动出牌策略"""
        structure = self.analyzer.analyze_hand_structure(hand_cards)

        # 根据难度选择不同的策略
        if self.difficulty == Difficulty.EASY:
            return self._easy_active_play(hand_cards, structure)
        elif self.difficulty == Difficulty.MEDIUM:
            return self._medium_active_play(hand_cards, structure, game_state)
        else:
            return self._hard_active_play(hand_cards, structure, game_state)

    def _easy_active_play(self, hand_cards: List[Card], structure: Dict[str, Any]) -> List[Card]:
        """简单难度主动出牌"""
        # 随机选择一种合理的出牌
        possible_plays = RuleEngine.find_possible_plays(hand_cards)

        if not possible_plays:
            # 如果没有找到，就出最小的单张
            smallest_card = min(hand_cards, key=lambda x: x.value)
            return [smallest_card]

        # 倾向于出小牌
        simple_plays = [play for play in possible_plays if len(play) <= 3]
        if simple_plays:
            return random.choice(simple_plays)

        return random.choice(possible_plays)

    def _medium_active_play(self, hand_cards: List[Card],
                          structure: Dict[str, Any], game_state: Dict[str, Any]) -> List[Card]:
        """中等难度主动出牌"""
        # 分析最佳组合
        combinations = self.analyzer.find_best_combinations(hand_cards)

        # 如果手牌很少，优先出大牌
        if len(hand_cards) <= 5:
            return self._choose_aggressive_play(hand_cards, structure)

        # 正常情况下选择合理的牌型
        if combinations:
            best_combo = combinations[0]
            if best_combo:
                return best_combo[0]

        # 备选方案：出单张
        singles = [c for c in hand_cards if c.value in structure["singles"]]
        if singles:
            # 出中等大小的单张
            mid_singles = [c for c in singles if 5 <= c.value <= 10]
            if mid_singles:
                return [random.choice(mid_singles)]
            return [min(singles, key=lambda x: x.value)]

        # 最后的备选：出最小的牌
        return [min(hand_cards, key=lambda x: x.value)]

    def _hard_active_play(self, hand_cards: List[Card],
                        structure: Dict[str, Any], game_state: Dict[str, Any]) -> List[Card]:
        """困难难度主动出牌"""
        # 分析当前局势
        opponents_cards = game_state.get("players_card_count", [])
        current_player_idx = game_state.get("current_player_idx", 0)

        # 计算其他玩家的手牌数
        other_players_cards = [count for i, count in enumerate(opponents_cards)
                             if i != current_player_idx]

        min_opponent_cards = min(other_players_cards) if other_players_cards else 17

        # 如果对手手牌很少，优先出大牌控制
        if min_opponent_cards <= 3:
            return self._choose_control_play(hand_cards, structure)

        # 如果自己手牌少，积极出牌
        if len(hand_cards) <= 5:
            return self._choose_aggressive_play(hand_cards, structure)

        # 正常情况下的最优策略
        return self._choose_optimal_play(hand_cards, structure, game_state)

    def _choose_follow_play(self, hand_cards: List[Card],
                          last_pattern: CardPattern,
                          game_state: Dict[str, Any]) -> Optional[List[Card]]:
        """跟牌策略"""
        # 找出所有可以跟的牌
        possible_plays = []
        for i in range(len(last_pattern.cards), len(hand_cards) + 1):
            from itertools import combinations
            for combo in combinations(hand_cards, i):
                if RuleEngine.can_follow(list(combo), last_pattern):
                    possible_plays.append(list(combo))

        if not possible_plays:
            return None  # 过牌

        # 根据难度选择跟牌策略
        if self.difficulty == Difficulty.EASY:
            return self._easy_follow_strategy(possible_plays, last_pattern)
        elif self.difficulty == Difficulty.MEDIUM:
            return self._medium_follow_strategy(possible_plays, last_pattern, game_state)
        else:
            return self._hard_follow_strategy(possible_plays, last_pattern, game_state)

    def _easy_follow_strategy(self, possible_plays: List[List[Card]],
                            last_pattern: CardPattern) -> Optional[List[Card]]:
        """简单难度跟牌策略"""
        if not possible_plays:
            return None

        # 70%概率选择跟牌 (更激进)
        if random.random() < 0.7:
            return None

        # 选择最小的能跟的牌
        return min(possible_plays, key=lambda x: sum(card.value for card in x))

    def _medium_follow_strategy(self, possible_plays: List[List[Card]],
                              last_pattern: CardPattern,
                              game_state: Dict[str, Any]) -> Optional[List[Card]]:
        """中等难度跟牌策略"""
        if not possible_plays:
            return None

        # 分析是否值得跟牌
        min_play = min(possible_plays, key=lambda x: sum(card.value for card in x))
        avg_value = sum(card.value for card in min_play) / len(min_play)

        # 如果需要出大牌才能跟，考虑放弃
        if avg_value > 13:  # 大于K (更激进)
            if random.random() < 0.6:  # 60%概率不跟 (更激进)
                return None

        return min_play

    def _hard_follow_strategy(self, possible_plays: List[List[Card]],
                            last_pattern: CardPattern,
                            game_state: Dict[str, Any]) -> Optional[List[Card]]:
        """困难难度跟牌策略"""
        if not possible_plays:
            return None

        # 复杂的决策逻辑
        last_player_idx = game_state.get("last_player_idx")
        current_player_idx = game_state.get("current_player_idx")
        players_card_count = game_state.get("players_card_count", [])

        # 判断出牌者的手牌数
        last_player_cards = players_card_count[last_player_idx] if last_player_idx is not None else 17

        # 如果上家手牌很少，必须压制
        if last_player_cards <= 3:
            return min(possible_plays, key=lambda x: sum(card.value for card in x))

        # 如果是队友（农民之间），更倾向于不跟
        current_is_landlord = game_state.get("landlord_idx") == current_player_idx
        last_is_landlord = game_state.get("landlord_idx") == last_player_idx

        if current_is_landlord == last_is_landlord:  # 同阵营
            if random.random() < 0.7:  # 70%概率不跟队友 (更激进)
                return None

        # 评估跟牌价值
        min_play = min(possible_plays, key=lambda x: sum(card.value for card in x))
        avg_value = sum(card.value for card in min_play) / len(min_play)

        # 根据牌的价值决定是否跟
        if avg_value <= 8:  # 小牌
            return min_play
        elif avg_value <= 12:  # 中等牌
            return min_play if random.random() < 0.7 else None  # 更激进
        else:  # 大牌
            return min_play if random.random() < 0.4 else None  # 更激进

    def _choose_aggressive_play(self, hand_cards: List[Card], structure: Dict[str, Any]) -> List[Card]:
        """积极出牌策略（手牌少时）"""
        # 优先出大牌
        if structure["bombs"]:
            bomb_value = structure["bombs"][0]
            bomb_cards = [c for c in hand_cards if c.value == bomb_value]
            return bomb_cards

        if structure["has_rockets"]:
            rocket_cards = [c for c in hand_cards if c.value in [16, 17]]
            return rocket_cards

        # 出最大的组合
        possible_plays = RuleEngine.find_possible_plays(hand_cards)
        if possible_plays:
            return max(possible_plays, key=lambda x: sum(card.value for card in x))

        return [max(hand_cards, key=lambda x: x.value)]

    def _choose_control_play(self, hand_cards: List[Card], structure: Dict[str, Any]) -> List[Card]:
        """控制性出牌策略（压制对手）"""
        # 出中等强度的牌来控制局面
        if structure["triples"]:
            triple_value = max(structure["triples"])
            triple_cards = [c for c in hand_cards if c.value == triple_value][:3]
            return triple_cards

        if structure["pairs"]:
            pair_value = max(structure["pairs"])
            pair_cards = [c for c in hand_cards if c.value == pair_value][:2]
            return pair_cards

        # 出大单张
        singles = [c for c in hand_cards if c.value in structure["singles"]]
        if singles:
            return [max(singles, key=lambda x: x.value)]

        return [max(hand_cards, key=lambda x: x.value)]

    def _choose_optimal_play(self, hand_cards: List[Card],
                           structure: Dict[str, Any], game_state: Dict[str, Any]) -> List[Card]:
        """最优出牌策略"""
        # 分析最佳组合
        combinations = self.analyzer.find_best_combinations(hand_cards)

        if combinations:
            best_combo = combinations[0]
            if best_combo:
                return best_combo[0]

        # 备选策略
        return self._medium_active_play(hand_cards, structure, game_state)


if __name__ == "__main__":
    # 测试代码
    from game.cards import create_cards_from_values

    test_cards = create_cards_from_values([3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17])

    strategy = AIStrategy(Difficulty.HARD)

    # 测试叫地主
    bottom = create_cards_from_values([15, 16, 17])
    will_bid = strategy.decide_landlord(test_cards, bottom)
    print(f"是否叫地主: {will_bid}")

    # 测试主动出牌
    game_state = {
        "current_player_idx": 0,
        "landlord_idx": 0,
        "players_card_count": [15, 12, 10]
    }

    play = strategy.choose_cards_to_play(test_cards, None, game_state)
    print(f"主动出牌: {[card.value for card in play]}")