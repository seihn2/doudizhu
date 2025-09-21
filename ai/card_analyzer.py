"""
AI牌型分析模块
为AI提供牌型分析、组合评估等功能
"""

from typing import List, Dict, Set, Tuple, Optional
from collections import Counter
from game.cards import Card
from game.rules import CardType, CardPattern, RuleEngine


class CardAnalyzer:
    """牌型分析器"""

    @staticmethod
    def analyze_hand_structure(cards: List[Card]) -> Dict[str, any]:
        """分析手牌结构"""
        values = [card.value for card in cards]
        value_count = Counter(values)

        structure = {
            "singles": [],      # 单张
            "pairs": [],        # 对子
            "triples": [],      # 三张
            "bombs": [],        # 炸弹
            "has_rockets": False,  # 是否有王炸
            "straight_potential": [],  # 顺子潜力
            "total_cards": len(cards)
        }

        # 分析各种牌型
        for value, count in value_count.items():
            if count == 1:
                structure["singles"].append(value)
            elif count == 2:
                structure["pairs"].append(value)
            elif count == 3:
                structure["triples"].append(value)
            elif count == 4:
                structure["bombs"].append(value)

        # 检查王炸
        if 16 in values and 17 in values:
            structure["has_rockets"] = True

        # 分析顺子潜力
        structure["straight_potential"] = CardAnalyzer._find_straight_potential(
            structure["singles"] + structure["pairs"] + structure["triples"]
        )

        return structure

    @staticmethod
    def _find_straight_potential(values: List[int]) -> List[Tuple[int, int]]:
        """找出顺子潜力"""
        if not values:
            return []

        # 过滤掉2和王
        valid_values = [v for v in values if v < 15]
        if len(valid_values) < 5:
            return []

        valid_values = sorted(set(valid_values))
        potential = []

        for start in range(len(valid_values) - 4):
            consecutive_count = 1
            for i in range(start + 1, len(valid_values)):
                if valid_values[i] == valid_values[i-1] + 1:
                    consecutive_count += 1
                else:
                    break

            if consecutive_count >= 5:
                potential.append((valid_values[start], consecutive_count))

        return potential

    @staticmethod
    def find_best_combinations(cards: List[Card]) -> List[List[Card]]:
        """找出最佳牌型组合"""
        values = [card.value for card in cards]
        combinations = []

        # 先找出所有可能的基础牌型
        basic_patterns = CardAnalyzer._find_basic_patterns(cards)

        # 评估每种组合的价值
        for pattern_cards in basic_patterns:
            remaining_cards = [c for c in cards if c not in pattern_cards]
            if remaining_cards:
                sub_combinations = CardAnalyzer.find_best_combinations(remaining_cards)
                for sub_combo in sub_combinations:
                    combinations.append([pattern_cards] + sub_combo)
            else:
                combinations.append([pattern_cards])

        # 按价值排序
        combinations.sort(key=lambda x: CardAnalyzer._evaluate_combination_value(x), reverse=True)
        return combinations[:10]  # 返回前10个最佳组合

    @staticmethod
    def _find_basic_patterns(cards: List[Card]) -> List[List[Card]]:
        """找出基础牌型"""
        patterns = []
        values = [card.value for card in cards]
        value_count = Counter(values)

        # 找炸弹
        for value, count in value_count.items():
            if count == 4:
                bomb_cards = [c for c in cards if c.value == value]
                patterns.append(bomb_cards)

        # 找王炸
        if 16 in values and 17 in values:
            rocket_cards = [c for c in cards if c.value in [16, 17]]
            patterns.append(rocket_cards)

        # 找三张及其组合
        triple_values = [value for value, count in value_count.items() if count >= 3]
        for value in triple_values:
            triple_cards = [c for c in cards if c.value == value][:3]
            patterns.append(triple_cards)

            # 三带一
            single_values = [v for v, count in value_count.items() if count >= 1 and v != value]
            for single_value in single_values:
                single_card = [c for c in cards if c.value == single_value][0]
                patterns.append(triple_cards + [single_card])

            # 三带对
            pair_values = [v for v, count in value_count.items() if count >= 2 and v != value]
            for pair_value in pair_values:
                pair_cards = [c for c in cards if c.value == pair_value][:2]
                patterns.append(triple_cards + pair_cards)

        # 找对子
        pair_values = [value for value, count in value_count.items() if count >= 2]
        for value in pair_values:
            pair_cards = [c for c in cards if c.value == value][:2]
            patterns.append(pair_cards)

        # 找顺子
        straight_patterns = CardAnalyzer._find_straights(cards)
        patterns.extend(straight_patterns)

        return patterns

    @staticmethod
    def _find_straights(cards: List[Card]) -> List[List[Card]]:
        """找出所有可能的顺子"""
        straights = []
        values = [card.value for card in cards if card.value < 15]  # 排除2和王
        value_count = Counter(values)

        sorted_values = sorted(value_count.keys())

        for start_idx in range(len(sorted_values)):
            for length in range(5, min(13, len(sorted_values) - start_idx + 1)):
                if start_idx + length > len(sorted_values):
                    break

                # 检查是否连续
                is_consecutive = True
                for i in range(length - 1):
                    if sorted_values[start_idx + i + 1] - sorted_values[start_idx + i] != 1:
                        is_consecutive = False
                        break

                if is_consecutive:
                    # 构建顺子
                    straight_cards = []
                    for i in range(length):
                        value = sorted_values[start_idx + i]
                        card = next(c for c in cards if c.value == value)
                        straight_cards.append(card)
                    straights.append(straight_cards)

        return straights

    @staticmethod
    def _evaluate_combination_value(combination: List[List[Card]]) -> float:
        """评估牌型组合的价值"""
        total_value = 0.0

        for pattern_cards in combination:
            pattern = RuleEngine.analyze_cards(pattern_cards)

            # 根据牌型给分
            type_scores = {
                CardType.SINGLE: 1.0,
                CardType.PAIR: 2.5,
                CardType.TRIPLE: 4.0,
                CardType.TRIPLE_WITH_SINGLE: 5.0,
                CardType.TRIPLE_WITH_PAIR: 6.0,
                CardType.STRAIGHT: 8.0,
                CardType.PAIR_STRAIGHT: 10.0,
                CardType.TRIPLE_STRAIGHT: 12.0,
                CardType.BOMB: 20.0,
                CardType.ROCKET: 25.0
            }

            base_score = type_scores.get(pattern.card_type, 0)

            # 根据牌值调整分数（大牌价值更高）
            value_bonus = pattern.main_value * 0.1

            total_value += base_score + value_bonus

        return total_value

    @staticmethod
    def calculate_winning_probability(cards: List[Card],
                                    opponents_card_counts: List[int],
                                    is_landlord: bool) -> float:
        """计算获胜概率"""
        hand_structure = CardAnalyzer.analyze_hand_structure(cards)

        # 基础评分
        base_score = 0.5

        # 手牌数量影响
        total_opponents_cards = sum(opponents_card_counts)
        if len(cards) < min(opponents_card_counts):
            base_score += 0.2  # 手牌少有优势

        # 强牌影响
        if hand_structure["has_rockets"]:
            base_score += 0.15
        if hand_structure["bombs"]:
            base_score += len(hand_structure["bombs"]) * 0.1

        # 牌型组合度影响
        combination_score = len(hand_structure["pairs"]) * 0.02 + \
                          len(hand_structure["triples"]) * 0.05 + \
                          len(hand_structure["straight_potential"]) * 0.03

        base_score += combination_score

        # 地主vs农民调整
        if is_landlord:
            base_score -= 0.1  # 地主处于劣势需要调整
        else:
            base_score += 0.05

        return min(max(base_score, 0.0), 1.0)

    @staticmethod
    def suggest_discard_strategy(cards: List[Card]) -> List[Card]:
        """建议拆牌策略"""
        structure = CardAnalyzer.analyze_hand_structure(cards)

        # 优先拆单张，特别是中等大小的单张
        singles_to_discard = [c for c in cards if c.value in structure["singles"]
                            and 7 <= c.value <= 12]

        if singles_to_discard:
            return singles_to_discard[:1]

        # 其次考虑拆对子
        if structure["pairs"]:
            pair_value = min(structure["pairs"])
            pair_cards = [c for c in cards if c.value == pair_value]
            return pair_cards[:1]

        # 最后考虑拆三张
        if structure["triples"]:
            triple_value = min(structure["triples"])
            triple_cards = [c for c in cards if c.value == triple_value]
            return triple_cards[:1]

        return []


if __name__ == "__main__":
    # 测试代码
    from game.cards import create_cards_from_values

    test_cards = create_cards_from_values([3, 4, 5, 6, 7, 3, 4, 8, 8, 8, 11, 11, 11, 15, 16, 17])

    analyzer = CardAnalyzer()
    structure = analyzer.analyze_hand_structure(test_cards)
    print("手牌结构分析:", structure)

    combinations = analyzer.find_best_combinations(test_cards)
    print(f"找到{len(combinations)}种组合方案")

    prob = analyzer.calculate_winning_probability(test_cards, [10, 12], True)
    print(f"获胜概率: {prob:.2%}")