"""
卡牌系统模块
实现斗地主游戏中的卡牌表示、洗牌、发牌等功能
"""

import random
from enum import Enum
from typing import List, Dict, Tuple
from dataclasses import dataclass


class Suit(Enum):
    """花色枚举"""
    SPADES = "♠"    # 黑桃
    HEARTS = "♥"    # 红桃
    DIAMONDS = "♦"  # 方块
    CLUBS = "♣"     # 梅花


@dataclass
class Card:
    """卡牌类"""
    value: int      # 牌值：3-15(3-K,A,2), 16(小王), 17(大王)
    suit: Suit = None  # 花色，王牌无花色

    def __str__(self) -> str:
        """返回卡牌的字符串表示"""
        if self.value == 16:
            return "小王"
        elif self.value == 17:
            return "大王"
        else:
            value_names = {
                3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
                11: "J", 12: "Q", 13: "K", 14: "A", 15: "2"
            }
            return f"{self.suit.value}{value_names[self.value]}"

    def __lt__(self, other) -> bool:
        """比较卡牌大小"""
        return self.value < other.value

    def __eq__(self, other) -> bool:
        """判断卡牌是否相等"""
        return self.value == other.value and self.suit == other.suit

    def __hash__(self) -> int:
        """哈希值，用于集合操作"""
        return hash((self.value, self.suit))


class Deck:
    """牌堆类"""

    def __init__(self):
        """初始化一副完整的54张牌"""
        self.cards: List[Card] = []
        self._create_deck()

    def _create_deck(self):
        """创建一副完整的牌"""
        self.cards = []

        # 创建普通牌 3-2
        for suit in Suit:
            for value in range(3, 16):  # 3到2
                self.cards.append(Card(value, suit))

        # 添加大小王
        self.cards.append(Card(16))  # 小王
        self.cards.append(Card(17))  # 大王

    def shuffle(self):
        """洗牌"""
        random.shuffle(self.cards)

    def deal_cards(self) -> Tuple[List[Card], List[Card], List[Card], List[Card]]:
        """发牌，返回三个玩家的手牌和底牌"""
        if len(self.cards) != 54:
            raise ValueError("牌数不正确，应该是54张")

        # 每人17张牌，剩余3张作为底牌
        player1_cards = self.cards[0:17]
        player2_cards = self.cards[17:34]
        player3_cards = self.cards[34:51]
        bottom_cards = self.cards[51:54]

        return player1_cards, player2_cards, player3_cards, bottom_cards

    def reset(self):
        """重置牌堆"""
        self._create_deck()


class Hand:
    """手牌类"""

    def __init__(self, cards: List[Card] = None):
        """初始化手牌"""
        self.cards: List[Card] = cards or []
        self.sort_cards()

    def add_cards(self, cards: List[Card]):
        """添加卡牌到手牌"""
        self.cards.extend(cards)
        self.sort_cards()

    def remove_cards(self, cards: List[Card]) -> bool:
        """从手牌中移除指定卡牌"""
        for card in cards:
            if card not in self.cards:
                return False

        for card in cards:
            self.cards.remove(card)

        return True

    def sort_cards(self):
        """对手牌进行排序"""
        self.cards.sort(key=lambda x: x.value)

    def get_card_count(self) -> Dict[int, int]:
        """获取各牌值的数量统计"""
        count = {}
        for card in self.cards:
            count[card.value] = count.get(card.value, 0) + 1
        return count

    def has_cards(self, cards: List[Card]) -> bool:
        """检查是否拥有指定的卡牌"""
        for card in cards:
            if card not in self.cards:
                return False
        return True

    def is_empty(self) -> bool:
        """检查手牌是否为空"""
        return len(self.cards) == 0

    def __len__(self) -> int:
        """返回手牌数量"""
        return len(self.cards)

    def __str__(self) -> str:
        """返回手牌的字符串表示"""
        return " ".join(str(card) for card in self.cards)


def create_cards_from_values(values: List[int]) -> List[Card]:
    """根据牌值列表创建卡牌列表（用于测试和AI决策）"""
    cards = []
    suits = [Suit.SPADES, Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS]

    for value in values:
        if value in [16, 17]:  # 王牌
            cards.append(Card(value))
        else:
            # 为普通牌分配花色（简单分配，实际游戏中花色不影响大小）
            suit = suits[(value - 3) % 4]
            cards.append(Card(value, suit))

    return cards


def values_to_string(values: List[int]) -> str:
    """将牌值列表转换为可读字符串"""
    value_names = {
        3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
        11: "J", 12: "Q", 13: "K", 14: "A", 15: "2", 16: "小王", 17: "大王"
    }
    return " ".join(value_names.get(v, str(v)) for v in values)


if __name__ == "__main__":
    # 测试代码
    deck = Deck()
    deck.shuffle()
    p1, p2, p3, bottom = deck.deal_cards()

    print("玩家1手牌:", " ".join(str(card) for card in p1))
    print("玩家2手牌:", " ".join(str(card) for card in p2))
    print("玩家3手牌:", " ".join(str(card) for card in p3))
    print("底牌:", " ".join(str(card) for card in bottom))