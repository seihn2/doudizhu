"""
游戏规则模块
实现斗地主的牌型识别、大小比较、出牌验证等核心规则
"""

from enum import Enum
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass
from .cards import Card


class CardType(Enum):
    """牌型枚举"""
    INVALID = "invalid"          # 无效牌型
    SINGLE = "single"            # 单张
    PAIR = "pair"                # 对子
    TRIPLE = "triple"            # 三张
    TRIPLE_WITH_SINGLE = "triple_with_single"    # 三带一
    TRIPLE_WITH_PAIR = "triple_with_pair"        # 三带对
    STRAIGHT = "straight"        # 顺子
    PAIR_STRAIGHT = "pair_straight"              # 连对
    TRIPLE_STRAIGHT = "triple_straight"          # 飞机
    TRIPLE_STRAIGHT_WITH_SINGLES = "triple_straight_with_singles"  # 飞机带单张
    TRIPLE_STRAIGHT_WITH_PAIRS = "triple_straight_with_pairs"      # 飞机带对子
    FOUR_WITH_TWO_SINGLES = "four_with_two_singles"  # 四带二单张
    FOUR_WITH_TWO_PAIRS = "four_with_two_pairs"      # 四带二对子
    BOMB = "bomb"                # 炸弹
    ROCKET = "rocket"            # 王炸


@dataclass
class CardPattern:
    """牌型类"""
    cards: List[Card]
    card_type: CardType
    main_value: int              # 主牌值（用于比较大小）
    length: int = 0              # 连续长度（用于顺子、连对等）

    def is_greater_than(self, other: 'CardPattern') -> bool:
        """比较两个牌型的大小"""
        # 王炸最大
        if self.card_type == CardType.ROCKET:
            return other.card_type != CardType.ROCKET

        # 炸弹比非炸弹大
        if self.card_type == CardType.BOMB:
            if other.card_type != CardType.BOMB and other.card_type != CardType.ROCKET:
                return True
            elif other.card_type == CardType.BOMB:
                return self.main_value > other.main_value
            else:
                return False

        # 其他牌型必须类型相同且张数相同才能比较
        if (self.card_type != other.card_type or
            len(self.cards) != len(other.cards)):
            return False

        # 比较主牌值
        return self.main_value > other.main_value


class RuleEngine:
    """规则引擎"""

    @staticmethod
    def analyze_cards(cards: List[Card]) -> CardPattern:
        """分析牌型"""
        if not cards:
            return CardPattern([], CardType.INVALID, 0)

        values = [card.value for card in cards]
        values.sort()
        value_count = {}
        for value in values:
            value_count[value] = value_count.get(value, 0) + 1

        card_count = len(cards)
        unique_values = len(value_count)

        # 单张
        if card_count == 1:
            return CardPattern(cards, CardType.SINGLE, values[0])

        # 对子
        if card_count == 2 and unique_values == 1:
            return CardPattern(cards, CardType.PAIR, values[0])

        # 王炸
        if card_count == 2 and 16 in values and 17 in values:
            return CardPattern(cards, CardType.ROCKET, 17)

        # 三张
        if card_count == 3 and unique_values == 1:
            return CardPattern(cards, CardType.TRIPLE, values[0])

        # 三带一
        if card_count == 4 and unique_values == 2:
            for value, count in value_count.items():
                if count == 3:
                    return CardPattern(cards, CardType.TRIPLE_WITH_SINGLE, value)

        # 三带对
        if card_count == 5 and unique_values == 2:
            triple_value = None
            pair_value = None
            for value, count in value_count.items():
                if count == 3:
                    triple_value = value
                elif count == 2:
                    pair_value = value
            if triple_value and pair_value:
                return CardPattern(cards, CardType.TRIPLE_WITH_PAIR, triple_value)

        # 炸弹
        if card_count == 4 and unique_values == 1:
            return CardPattern(cards, CardType.BOMB, values[0])

        # 四带二单张
        if card_count == 6 and unique_values == 3:
            four_value = None
            for value, count in value_count.items():
                if count == 4:
                    four_value = value
                    break
            if four_value:
                return CardPattern(cards, CardType.FOUR_WITH_TWO_SINGLES, four_value)

        # 四带二对子
        if card_count == 8 and unique_values == 3:
            four_value = None
            pair_count = 0
            for value, count in value_count.items():
                if count == 4:
                    four_value = value
                elif count == 2:
                    pair_count += 1
            if four_value and pair_count == 2:
                return CardPattern(cards, CardType.FOUR_WITH_TWO_PAIRS, four_value)

        # 顺子（至少5张）
        if card_count >= 5 and unique_values == card_count:
            if RuleEngine._is_straight(values):
                return CardPattern(cards, CardType.STRAIGHT, values[-1], card_count)

        # 连对（至少3对）
        if card_count >= 6 and card_count % 2 == 0 and unique_values == card_count // 2:
            if all(count == 2 for count in value_count.values()):
                sorted_values = sorted(value_count.keys())
                if RuleEngine._is_straight(sorted_values):
                    return CardPattern(cards, CardType.PAIR_STRAIGHT, sorted_values[-1], len(sorted_values))

        # 飞机相关
        triple_values = [value for value, count in value_count.items() if count == 3]
        if len(triple_values) >= 2:
            triple_values.sort()
            if RuleEngine._is_straight(triple_values):
                # 纯飞机
                if card_count == len(triple_values) * 3:
                    return CardPattern(cards, CardType.TRIPLE_STRAIGHT, triple_values[-1], len(triple_values))
                # 飞机带单张
                elif card_count == len(triple_values) * 4:
                    return CardPattern(cards, CardType.TRIPLE_STRAIGHT_WITH_SINGLES, triple_values[-1], len(triple_values))
                # 飞机带对子
                elif card_count == len(triple_values) * 5:
                    return CardPattern(cards, CardType.TRIPLE_STRAIGHT_WITH_PAIRS, triple_values[-1], len(triple_values))

        return CardPattern(cards, CardType.INVALID, 0)

    @staticmethod
    def _is_straight(values: List[int]) -> bool:
        """检查是否为连续序列"""
        if len(values) < 2:
            return False

        # 不能包含2和王
        if any(value >= 15 for value in values):
            return False

        # 检查是否连续
        for i in range(1, len(values)):
            if values[i] - values[i-1] != 1:
                return False

        return True

    @staticmethod
    def can_follow(current_cards: List[Card], last_pattern: CardPattern) -> bool:
        """检查当前出牌是否可以跟上一手牌"""
        if not last_pattern or last_pattern.card_type == CardType.INVALID:
            return True

        current_pattern = RuleEngine.analyze_cards(current_cards)
        if current_pattern.card_type == CardType.INVALID:
            return False

        return current_pattern.is_greater_than(last_pattern)

    @staticmethod
    def is_valid_cards(cards: List[Card]) -> bool:
        """检查出牌是否合法"""
        pattern = RuleEngine.analyze_cards(cards)
        return pattern.card_type != CardType.INVALID

    @staticmethod
    def get_card_type_name(card_type: CardType) -> str:
        """获取牌型的中文名称"""
        names = {
            CardType.SINGLE: "单张",
            CardType.PAIR: "对子",
            CardType.TRIPLE: "三张",
            CardType.TRIPLE_WITH_SINGLE: "三带一",
            CardType.TRIPLE_WITH_PAIR: "三带对",
            CardType.STRAIGHT: "顺子",
            CardType.PAIR_STRAIGHT: "连对",
            CardType.TRIPLE_STRAIGHT: "飞机",
            CardType.TRIPLE_STRAIGHT_WITH_SINGLES: "飞机带单张",
            CardType.TRIPLE_STRAIGHT_WITH_PAIRS: "飞机带对子",
            CardType.FOUR_WITH_TWO_SINGLES: "四带二",
            CardType.FOUR_WITH_TWO_PAIRS: "四带二对",
            CardType.BOMB: "炸弹",
            CardType.ROCKET: "王炸",
            CardType.INVALID: "无效牌型"
        }
        return names.get(card_type, "未知牌型")

    @staticmethod
    def find_possible_plays(hand_cards: List[Card], last_pattern: Optional[CardPattern] = None) -> List[List[Card]]:
        """找出手牌中所有可能的出牌组合"""
        possible_plays = []

        if not last_pattern:
            # 如果是首次出牌，找出所有有效的牌型
            for i in range(1, len(hand_cards) + 1):
                from itertools import combinations
                for combo in combinations(hand_cards, i):
                    if RuleEngine.is_valid_cards(list(combo)):
                        possible_plays.append(list(combo))
        else:
            # 找出能够跟上上一手牌的组合
            for i in range(len(last_pattern.cards), len(hand_cards) + 1):
                from itertools import combinations
                for combo in combinations(hand_cards, i):
                    if RuleEngine.can_follow(list(combo), last_pattern):
                        possible_plays.append(list(combo))

        return possible_plays


if __name__ == "__main__":
    # 测试代码
    from .cards import create_cards_from_values

    # 测试各种牌型
    test_cases = [
        ([3], "单张"),
        ([3, 3], "对子"),
        ([3, 3, 3], "三张"),
        ([3, 3, 3, 4], "三带一"),
        ([3, 3, 3, 4, 4], "三带对"),
        ([3, 4, 5, 6, 7], "顺子"),
        ([3, 3, 4, 4, 5, 5], "连对"),
        ([3, 3, 3, 4, 4, 4], "飞机"),
        ([8, 8, 8, 8], "炸弹"),
        ([16, 17], "王炸"),
    ]

    for values, expected in test_cases:
        cards = create_cards_from_values(values)
        pattern = RuleEngine.analyze_cards(cards)
        print(f"{values} -> {RuleEngine.get_card_type_name(pattern.card_type)} (期望: {expected})")