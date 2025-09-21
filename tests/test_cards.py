"""
卡牌系统测试
"""

import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from game.cards import Card, Deck, Hand, Suit, create_cards_from_values


class TestCard(unittest.TestCase):
    """测试Card类"""

    def test_card_creation(self):
        """测试卡牌创建"""
        card = Card(3, Suit.SPADES)
        self.assertEqual(card.value, 3)
        self.assertEqual(card.suit, Suit.SPADES)

    def test_card_comparison(self):
        """测试卡牌比较"""
        card1 = Card(3, Suit.SPADES)
        card2 = Card(4, Suit.HEARTS)
        card3 = Card(3, Suit.CLUBS)

        self.assertTrue(card1 < card2)
        self.assertFalse(card2 < card1)
        self.assertFalse(card1 < card3)

    def test_jokers(self):
        """测试王牌"""
        small_joker = Card(16)
        big_joker = Card(17)

        self.assertEqual(str(small_joker), "小王")
        self.assertEqual(str(big_joker), "大王")
        self.assertTrue(small_joker < big_joker)


class TestDeck(unittest.TestCase):
    """测试Deck类"""

    def test_deck_creation(self):
        """测试牌堆创建"""
        deck = Deck()
        self.assertEqual(len(deck.cards), 54)

    def test_deal_cards(self):
        """测试发牌"""
        deck = Deck()
        p1, p2, p3, bottom = deck.deal_cards()

        self.assertEqual(len(p1), 17)
        self.assertEqual(len(p2), 17)
        self.assertEqual(len(p3), 17)
        self.assertEqual(len(bottom), 3)

        # 检查总牌数
        total_cards = len(p1) + len(p2) + len(p3) + len(bottom)
        self.assertEqual(total_cards, 54)

    def test_shuffle(self):
        """测试洗牌"""
        deck1 = Deck()
        deck2 = Deck()

        original_order = [card.value for card in deck1.cards]
        deck2.shuffle()
        shuffled_order = [card.value for card in deck2.cards]

        # 洗牌后顺序应该不同（概率极高）
        self.assertNotEqual(original_order, shuffled_order)


class TestHand(unittest.TestCase):
    """测试Hand类"""

    def test_hand_creation(self):
        """测试手牌创建"""
        cards = create_cards_from_values([3, 4, 5])
        hand = Hand(cards)

        self.assertEqual(len(hand), 3)
        self.assertFalse(hand.is_empty())

    def test_add_remove_cards(self):
        """测试添加和移除卡牌"""
        hand = Hand()
        cards = create_cards_from_values([3, 4, 5])

        hand.add_cards(cards)
        self.assertEqual(len(hand), 3)

        # 移除一张牌
        success = hand.remove_cards([cards[0]])
        self.assertTrue(success)
        self.assertEqual(len(hand), 2)

        # 尝试移除不存在的牌
        non_existent = create_cards_from_values([10])
        success = hand.remove_cards(non_existent)
        self.assertFalse(success)

    def test_card_count(self):
        """测试牌值统计"""
        cards = create_cards_from_values([3, 3, 4, 4, 4, 5])
        hand = Hand(cards)

        count = hand.get_card_count()
        self.assertEqual(count[3], 2)
        self.assertEqual(count[4], 3)
        self.assertEqual(count[5], 1)


class TestUtilityFunctions(unittest.TestCase):
    """测试工具函数"""

    def test_create_cards_from_values(self):
        """测试根据牌值创建卡牌"""
        values = [3, 4, 5, 16, 17]
        cards = create_cards_from_values(values)

        self.assertEqual(len(cards), 5)
        self.assertEqual(cards[0].value, 3)
        self.assertEqual(cards[3].value, 16)  # 小王
        self.assertEqual(cards[4].value, 17)  # 大王

        # 检查王牌没有花色
        self.assertIsNone(cards[3].suit)
        self.assertIsNone(cards[4].suit)


if __name__ == '__main__':
    unittest.main()