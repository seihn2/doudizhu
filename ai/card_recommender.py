"""
出牌推荐系统
为人类玩家提供智能的出牌建议
"""

from typing import List, Optional, Dict, Tuple
from collections import Counter
from game.cards import Card
from game.rules import CardPattern, CardType, RuleEngine
from .card_analyzer import CardAnalyzer


class CardRecommender:
    """出牌推荐器"""

    def __init__(self):
        self.analyzer = CardAnalyzer()

    def get_recommendations(self, hand_cards: List[Card],
                          last_pattern: Optional[CardPattern] = None,
                          game_state: Dict = None,
                          max_suggestions: int = 5) -> List[Dict]:
        """
        获取出牌推荐

        Args:
            hand_cards: 手牌
            last_pattern: 上一手牌
            game_state: 游戏状态
            max_suggestions: 最大推荐数量

        Returns:
            推荐列表，每个推荐包含：
            {
                'cards': List[Card],
                'description': str,
                'reason': str,
                'priority': float,
                'risk_level': str
            }
        """
        recommendations = []

        if last_pattern is None:
            # 主动出牌推荐
            recommendations = self._get_active_play_recommendations(hand_cards, game_state)
        else:
            # 跟牌推荐
            recommendations = self._get_follow_play_recommendations(hand_cards, last_pattern, game_state)

        # 按优先级排序并限制数量
        recommendations.sort(key=lambda x: x['priority'], reverse=True)
        return recommendations[:max_suggestions]

    def _get_active_play_recommendations(self, hand_cards: List[Card],
                                       game_state: Dict = None) -> List[Dict]:
        """获取主动出牌推荐"""
        recommendations = []
        structure = self.analyzer.analyze_hand_structure(hand_cards)

        # 分析其他玩家手牌数
        opponent_cards = []
        if game_state:
            players_card_count = game_state.get('players_card_count', [])
            current_idx = game_state.get('current_player_idx', 0)
            opponent_cards = [count for i, count in enumerate(players_card_count) if i != current_idx]

        min_opponent_cards = min(opponent_cards) if opponent_cards else 17

        # 策略1: 如果对手剩牌很少，出大牌控制
        if min_opponent_cards <= 5:
            control_recs = self._get_control_recommendations(hand_cards, structure)
            recommendations.extend(control_recs)

        # 策略2: 如果自己牌少，积极出牌
        if len(hand_cards) <= 8:
            aggressive_recs = self._get_aggressive_recommendations(hand_cards, structure)
            recommendations.extend(aggressive_recs)

        # 策略3: 正常情况下的优化出牌
        optimal_recs = self._get_optimal_active_recommendations(hand_cards, structure)
        recommendations.extend(optimal_recs)

        return recommendations

    def _get_follow_play_recommendations(self, hand_cards: List[Card],
                                       last_pattern: CardPattern,
                                       game_state: Dict = None) -> List[Dict]:
        """获取跟牌推荐"""
        recommendations = []

        # 找出所有可以跟的牌
        possible_plays = RuleEngine.find_possible_plays(hand_cards, last_pattern)

        if not possible_plays:
            # 无法跟牌，建议过牌
            recommendations.append({
                'cards': [],
                'description': '过牌',
                'reason': '没有合适的牌可以跟，建议过牌等待机会',
                'priority': 5.0,
                'risk_level': '安全'
            })
            return recommendations

        # 分析每种跟牌方案
        for play_cards in possible_plays:
            pattern = RuleEngine.analyze_cards(play_cards)
            priority, reason, risk = self._evaluate_follow_play(
                play_cards, pattern, hand_cards, last_pattern, game_state
            )

            recommendations.append({
                'cards': play_cards,
                'description': RuleEngine.get_card_type_name(pattern.card_type),
                'reason': reason,
                'priority': priority,
                'risk_level': risk
            })

        # 添加过牌选项
        pass_priority, pass_reason = self._evaluate_pass_option(last_pattern, game_state)
        recommendations.append({
            'cards': [],
            'description': '过牌',
            'reason': pass_reason,
            'priority': pass_priority,
            'risk_level': '安全'
        })

        return recommendations

    def _get_control_recommendations(self, hand_cards: List[Card],
                                   structure: Dict) -> List[Dict]:
        """获取控制性出牌推荐"""
        recommendations = []

        # 推荐炸弹
        if structure['bombs']:
            bomb_value = structure['bombs'][0]
            bomb_cards = [c for c in hand_cards if c.value == bomb_value]
            recommendations.append({
                'cards': bomb_cards,
                'description': '炸弹',
                'reason': '对手手牌较少，用炸弹控制局面',
                'priority': 9.0,
                'risk_level': '高风险高回报'
            })

        # 推荐王炸
        if structure['has_rockets']:
            rocket_cards = [c for c in hand_cards if c.value in [16, 17]]
            recommendations.append({
                'cards': rocket_cards,
                'description': '王炸',
                'reason': '对手即将获胜，使用王炸夺取主动权',
                'priority': 10.0,
                'risk_level': '高风险高回报'
            })

        # 推荐大的三张
        if structure['triples']:
            large_triples = [v for v in structure['triples'] if v >= 12]
            if large_triples:
                triple_value = max(large_triples)
                triple_cards = [c for c in hand_cards if c.value == triple_value][:3]
                recommendations.append({
                    'cards': triple_cards,
                    'description': '三张',
                    'reason': f'出大三张({self._value_to_name(triple_value)})控制场面',
                    'priority': 7.5,
                    'risk_level': '中等风险'
                })

        return recommendations

    def _get_aggressive_recommendations(self, hand_cards: List[Card],
                                      structure: Dict) -> List[Dict]:
        """获取积极出牌推荐"""
        recommendations = []

        # 找出最大的牌型组合
        combinations = self.analyzer.find_best_combinations(hand_cards)

        if combinations and combinations[0]:
            best_combo = combinations[0][0]
            pattern = RuleEngine.analyze_cards(best_combo)

            recommendations.append({
                'cards': best_combo,
                'description': RuleEngine.get_card_type_name(pattern.card_type),
                'reason': '手牌较少，选择最优组合快速清牌',
                'priority': 8.0,
                'risk_level': '中等风险'
            })

        # 推荐顺子和连对
        straights = self._find_straights_in_hand(hand_cards)
        for straight in straights:
            if len(straight) >= 5:
                recommendations.append({
                    'cards': straight,
                    'description': '顺子',
                    'reason': f'一次性出{len(straight)}张牌，快速减少手牌',
                    'priority': 7.0,
                    'risk_level': '低风险'
                })

        return recommendations

    def _get_optimal_active_recommendations(self, hand_cards: List[Card],
                                          structure: Dict) -> List[Dict]:
        """获取优化的主动出牌推荐"""
        recommendations = []

        # 推荐单张（从小到大）
        if structure['singles']:
            small_singles = [v for v in structure['singles'] if v <= 10]
            if small_singles:
                single_value = min(small_singles)
                single_card = next(c for c in hand_cards if c.value == single_value)
                recommendations.append({
                    'cards': [single_card],
                    'description': '单张',
                    'reason': f'出小单张({self._value_to_name(single_value)})试探',
                    'priority': 6.0,
                    'risk_level': '低风险'
                })

        # 推荐对子
        if structure['pairs']:
            small_pairs = [v for v in structure['pairs'] if v <= 10]
            if small_pairs:
                pair_value = min(small_pairs)
                pair_cards = [c for c in hand_cards if c.value == pair_value][:2]
                recommendations.append({
                    'cards': pair_cards,
                    'description': '对子',
                    'reason': f'出小对子({self._value_to_name(pair_value)})，保留大牌',
                    'priority': 5.5,
                    'risk_level': '低风险'
                })

        # 推荐三带一
        if structure['triples']:
            for triple_value in structure['triples']:
                triple_cards = [c for c in hand_cards if c.value == triple_value][:3]

                # 找单张配牌
                available_singles = [v for v in structure['singles'] if v != triple_value]
                if available_singles:
                    single_value = min(available_singles)
                    single_card = next(c for c in hand_cards if c.value == single_value)

                    combo_cards = triple_cards + [single_card]
                    recommendations.append({
                        'cards': combo_cards,
                        'description': '三带一',
                        'reason': f'三带一组合，高效利用手牌',
                        'priority': 6.5,
                        'risk_level': '低风险'
                    })

        return recommendations

    def _evaluate_follow_play(self, play_cards: List[Card], pattern: CardPattern,
                            hand_cards: List[Card], last_pattern: CardPattern,
                            game_state: Dict = None) -> Tuple[float, str, str]:
        """评估跟牌方案"""
        priority = 5.0
        reason = "可以跟牌"
        risk = "中等风险"

        # 计算牌值平均值
        avg_value = sum(card.value for card in play_cards) / len(play_cards)

        # 如果是小牌，优先级高
        if avg_value <= 8:
            priority += 2.0
            reason = "使用小牌跟牌，保留大牌"
            risk = "低风险"
        elif avg_value >= 13:
            priority -= 1.0
            reason = "需要使用大牌，考虑是否值得"
            risk = "高风险"

        # 炸弹和王炸特殊处理
        if pattern.card_type == CardType.BOMB:
            priority += 3.0
            reason = "炸弹可以压制对手，获得出牌权"
            risk = "高风险高回报"
        elif pattern.card_type == CardType.ROCKET:
            priority += 4.0
            reason = "王炸必胜，夺取绝对控制权"
            risk = "高风险高回报"

        # 根据剩余手牌数调整
        remaining_cards = len(hand_cards) - len(play_cards)
        if remaining_cards <= 3:
            priority += 1.5
            reason += "，有机会快速获胜"

        return priority, reason, risk

    def _evaluate_pass_option(self, last_pattern: CardPattern,
                            game_state: Dict = None) -> Tuple[float, str]:
        """评估过牌选项"""
        priority = 4.0
        reason = "保留手牌，等待更好机会"

        # 如果上一手牌很大，过牌优先级提高
        if last_pattern and last_pattern.main_value >= 14:  # A或以上
            priority += 1.5
            reason = "对手出大牌，过牌等待机会"

        # 如果是炸弹或王炸，过牌优先级更高
        if last_pattern and last_pattern.card_type in [CardType.BOMB, CardType.ROCKET]:
            priority += 2.0
            reason = "对手出炸弹/王炸，建议过牌"

        return priority, reason

    def _find_straights_in_hand(self, hand_cards: List[Card]) -> List[List[Card]]:
        """在手牌中找顺子"""
        straights = []
        values = [card.value for card in hand_cards if card.value < 15]  # 排除2和王
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
                        card = next(c for c in hand_cards if c.value == value)
                        straight_cards.append(card)
                    straights.append(straight_cards)

        return straights

    def _value_to_name(self, value: int) -> str:
        """将牌值转换为名称"""
        names = {
            3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
            11: "J", 12: "Q", 13: "K", 14: "A", 15: "2", 16: "小王", 17: "大王"
        }
        return names.get(value, str(value))

    def format_recommendation(self, rec: Dict) -> str:
        """格式化推荐输出"""
        if not rec['cards']:
            return f"- {rec['description']}: {rec['reason']} (风险: {rec['risk_level']})"

        card_names = [str(card) for card in rec['cards']]
        cards_str = " ".join(card_names)
        return f"- {rec['description']}: {cards_str} - {rec['reason']} (风险: {rec['risk_level']})"


if __name__ == "__main__":
    # 测试推荐系统
    from game.cards import create_cards_from_values

    # 创建测试手牌
    test_cards = create_cards_from_values([3, 4, 5, 6, 7, 8, 8, 8, 11, 11, 14, 15, 16, 17])

    recommender = CardRecommender()

    print("=== 主动出牌推荐 ===")
    recs = recommender.get_recommendations(test_cards)
    for i, rec in enumerate(recs, 1):
        print(f"{i}. {recommender.format_recommendation(rec)}")

    print("\n=== 跟单张7的推荐 ===")
    from game.rules import RuleEngine
    last_cards = create_cards_from_values([7])
    last_pattern = RuleEngine.analyze_cards(last_cards)

    recs = recommender.get_recommendations(test_cards, last_pattern)
    for i, rec in enumerate(recs, 1):
        print(f"{i}. {recommender.format_recommendation(rec)}")