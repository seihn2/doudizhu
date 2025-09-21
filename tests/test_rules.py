"""
游戏规则测试
"""

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from game.rules import RuleEngine, CardType, CardPattern
from game.cards import create_cards_from_values


class TestRuleEngine(unittest.TestCase):
    """测试规则引擎"""

    def test_single_card(self):
        """测试单张"""
        cards = create_cards_from_values([7])
        pattern = RuleEngine.analyze_cards(cards)

        self.assertEqual(pattern.card_type, CardType.SINGLE)
        self.assertEqual(pattern.main_value, 7)

    def test_pair(self):
        """测试对子"""
        cards = create_cards_from_values([7, 7])
        pattern = RuleEngine.analyze_cards(cards)

        self.assertEqual(pattern.card_type, CardType.PAIR)
        self.assertEqual(pattern.main_value, 7)

    def test_triple(self):
        """测试三张"""
        cards = create_cards_from_values([7, 7, 7])
        pattern = RuleEngine.analyze_cards(cards)

        self.assertEqual(pattern.card_type, CardType.TRIPLE)
        self.assertEqual(pattern.main_value, 7)

    def test_triple_with_single(self):
        """测试三带一"""
        cards = create_cards_from_values([7, 7, 7, 3])
        pattern = RuleEngine.analyze_cards(cards)

        self.assertEqual(pattern.card_type, CardType.TRIPLE_WITH_SINGLE)
        self.assertEqual(pattern.main_value, 7)

    def test_triple_with_pair(self):
        """测试三带对"""
        cards = create_cards_from_values([7, 7, 7, 3, 3])
        pattern = RuleEngine.analyze_cards(cards)

        self.assertEqual(pattern.card_type, CardType.TRIPLE_WITH_PAIR)
        self.assertEqual(pattern.main_value, 7)

    def test_straight(self):
        """测试顺子"""
        cards = create_cards_from_values([3, 4, 5, 6, 7])
        pattern = RuleEngine.analyze_cards(cards)

        self.assertEqual(pattern.card_type, CardType.STRAIGHT)
        self.assertEqual(pattern.main_value, 7)
        self.assertEqual(pattern.length, 5)

    def test_pair_straight(self):
        """测试连对"""
        cards = create_cards_from_values([3, 3, 4, 4, 5, 5])
        pattern = RuleEngine.analyze_cards(cards)

        self.assertEqual(pattern.card_type, CardType.PAIR_STRAIGHT)
        self.assertEqual(pattern.main_value, 5)

    def test_bomb(self):
        """测试炸弹"""
        cards = create_cards_from_values([7, 7, 7, 7])
        pattern = RuleEngine.analyze_cards(cards)

        self.assertEqual(pattern.card_type, CardType.BOMB)
        self.assertEqual(pattern.main_value, 7)

    def test_rocket(self):
        """测试王炸"""
        cards = create_cards_from_values([16, 17])
        pattern = RuleEngine.analyze_cards(cards)

        self.assertEqual(pattern.card_type, CardType.ROCKET)
        self.assertEqual(pattern.main_value, 17)

    def test_invalid_straight_with_2(self):
        """测试包含2的无效顺子"""
        cards = create_cards_from_values([13, 14, 15, 3, 4])  # K, A, 2, 3, 4
        pattern = RuleEngine.analyze_cards(cards)

        self.assertEqual(pattern.card_type, CardType.INVALID)

    def test_invalid_cards(self):
        """测试无效牌型"""
        # 无效的三带一（需要3+1张）
        cards = create_cards_from_values([7, 7, 3, 4])
        pattern = RuleEngine.analyze_cards(cards)
        self.assertEqual(pattern.card_type, CardType.INVALID)

        # 太短的顺子
        cards = create_cards_from_values([3, 4, 5, 6])
        pattern = RuleEngine.analyze_cards(cards)
        self.assertEqual(pattern.card_type, CardType.INVALID)


class TestCardPatternComparison(unittest.TestCase):
    """测试牌型比较"""

    def test_same_type_comparison(self):
        """测试相同类型牌型比较"""
        cards1 = create_cards_from_values([7])
        cards2 = create_cards_from_values([8])

        pattern1 = RuleEngine.analyze_cards(cards1)
        pattern2 = RuleEngine.analyze_cards(cards2)

        self.assertTrue(pattern2.is_greater_than(pattern1))
        self.assertFalse(pattern1.is_greater_than(pattern2))

    def test_bomb_beats_normal(self):
        """测试炸弹打普通牌型"""
        bomb_cards = create_cards_from_values([3, 3, 3, 3])
        normal_cards = create_cards_from_values([14, 14, 14])  # 三个A

        bomb_pattern = RuleEngine.analyze_cards(bomb_cards)
        normal_pattern = RuleEngine.analyze_cards(normal_cards)

        self.assertTrue(bomb_pattern.is_greater_than(normal_pattern))
        self.assertFalse(normal_pattern.is_greater_than(bomb_pattern))

    def test_rocket_beats_bomb(self):
        """测试王炸打炸弹"""
        rocket_cards = create_cards_from_values([16, 17])
        bomb_cards = create_cards_from_values([14, 14, 14, 14])  # 四个A

        rocket_pattern = RuleEngine.analyze_cards(rocket_cards)
        bomb_pattern = RuleEngine.analyze_cards(bomb_cards)

        self.assertTrue(rocket_pattern.is_greater_than(bomb_pattern))
        self.assertFalse(bomb_pattern.is_greater_than(rocket_pattern))

    def test_different_type_cannot_compare(self):
        """测试不同类型不能比较"""
        single_cards = create_cards_from_values([7])
        pair_cards = create_cards_from_values([6, 6])

        single_pattern = RuleEngine.analyze_cards(single_cards)
        pair_pattern = RuleEngine.analyze_cards(pair_cards)

        self.assertFalse(single_pattern.is_greater_than(pair_pattern))
        self.assertFalse(pair_pattern.is_greater_than(single_pattern))


class TestCanFollow(unittest.TestCase):
    """测试跟牌规则"""

    def test_can_follow_same_type(self):
        """测试可以跟相同类型"""
        last_cards = create_cards_from_values([7])
        current_cards = create_cards_from_values([8])

        last_pattern = RuleEngine.analyze_cards(last_cards)
        can_follow = RuleEngine.can_follow(current_cards, last_pattern)

        self.assertTrue(can_follow)

    def test_cannot_follow_smaller(self):
        """测试不能跟更小的牌"""
        last_cards = create_cards_from_values([8])
        current_cards = create_cards_from_values([7])

        last_pattern = RuleEngine.analyze_cards(last_cards)
        can_follow = RuleEngine.can_follow(current_cards, last_pattern)

        self.assertFalse(can_follow)

    def test_bomb_can_follow_anything(self):
        """测试炸弹可以跟任何牌"""
        last_cards = create_cards_from_values([14, 14, 14])  # 三个A
        bomb_cards = create_cards_from_values([3, 3, 3, 3])

        last_pattern = RuleEngine.analyze_cards(last_cards)
        can_follow = RuleEngine.can_follow(bomb_cards, last_pattern)

        self.assertTrue(can_follow)


if __name__ == '__main__':
    unittest.main()