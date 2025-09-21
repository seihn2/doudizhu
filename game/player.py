"""
玩家基类模块
定义玩家的基本属性和行为接口
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from .cards import Card, Hand
from .rules import CardPattern


class Player(ABC):
    """玩家基类"""

    def __init__(self, name: str, player_id: int):
        """初始化玩家"""
        self.name = name
        self.player_id = player_id
        self.hand = Hand()
        self.is_landlord = False
        self.score = 0

    def receive_cards(self, cards: List[Card]):
        """接收卡牌"""
        self.hand.add_cards(cards)

    def play_cards(self, cards: List[Card]) -> bool:
        """出牌"""
        if self.hand.has_cards(cards):
            self.hand.remove_cards(cards)
            return True
        return False

    def get_hand_cards(self) -> List[Card]:
        """获取手牌"""
        return self.hand.cards.copy()

    def get_card_count(self) -> int:
        """获取手牌数量"""
        return len(self.hand.cards)

    def is_hand_empty(self) -> bool:
        """检查是否已出完所有手牌"""
        return self.hand.is_empty()

    def set_landlord(self, is_landlord: bool):
        """设置是否为地主"""
        self.is_landlord = is_landlord

    @abstractmethod
    def decide_landlord(self, bottom_cards: List[Card]) -> bool:
        """决定是否要当地主"""
        pass

    @abstractmethod
    def choose_cards_to_play(self, last_pattern: Optional[CardPattern],
                           game_state: dict) -> Optional[List[Card]]:
        """选择要出的牌"""
        pass

    def __str__(self) -> str:
        """返回玩家信息"""
        role = "地主" if self.is_landlord else "农民"
        return f"{self.name}({role}) - {len(self.hand.cards)}张牌"


class HumanPlayer(Player):
    """人类玩家"""

    def __init__(self, name: str, player_id: int):
        super().__init__(name, player_id)

    def decide_landlord(self, bottom_cards: List[Card]) -> bool:
        """决定是否要当地主（需要用户输入）"""
        print(f"\n{self.name}，是否要当地主？")
        print("底牌：", " ".join(str(card) for card in bottom_cards))
        print("你的手牌：", str(self.hand))

        while True:
            choice = input("请选择 (y/n): ").strip().lower()
            if choice in ['y', 'yes', '是', '要']:
                return True
            elif choice in ['n', 'no', '否', '不要']:
                return False
            else:
                print("请输入有效选择")

    def choose_cards_to_play(self, last_pattern: Optional[CardPattern],
                           game_state: dict) -> Optional[List[Card]]:
        """选择要出的牌（需要用户输入）"""
        print(f"\n轮到{self.name}出牌")
        print("你的手牌：", str(self.hand))

        if last_pattern:
            from .rules import RuleEngine
            print(f"上家出牌：{RuleEngine.get_card_type_name(last_pattern.card_type)} - ",
                  " ".join(str(card) for card in last_pattern.cards))

        while True:
            choice = input("请输入要出的牌（用空格分隔，如：3 4 5，输入'pass'跳过）: ").strip()

            if choice.lower() in ['pass', 'p', '过', '跳过']:
                return None

            try:
                # 解析用户输入
                cards_to_play = self._parse_input(choice)
                if cards_to_play and self.hand.has_cards(cards_to_play):
                    from .rules import RuleEngine
                    if last_pattern is None or RuleEngine.can_follow(cards_to_play, last_pattern):
                        return cards_to_play
                    else:
                        print("这手牌无法跟上一手牌，请重新选择")
                else:
                    print("无效的牌或你没有这些牌，请重新输入")
            except ValueError:
                print("输入格式错误，请重新输入")

    def _parse_input(self, input_str: str) -> List[Card]:
        """解析用户输入的牌"""
        if not input_str.strip():
            return []

        parts = input_str.split()
        cards_to_play = []

        value_map = {
            '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
            'j': 11, 'q': 12, 'k': 13, 'a': 14, '2': 15,
            '小王': 16, '大王': 17, 'joker': 16, 'JOKER': 17
        }

        for part in parts:
            part = part.lower()
            if part in value_map:
                value = value_map[part]
                # 在手牌中找到对应的牌
                for card in self.hand.cards:
                    if card.value == value and card not in cards_to_play:
                        cards_to_play.append(card)
                        break

        return cards_to_play


if __name__ == "__main__":
    # 测试代码
    from .cards import Deck

    deck = Deck()
    deck.shuffle()
    p1_cards, _, _, bottom = deck.deal_cards()

    player = HumanPlayer("测试玩家", 0)
    player.receive_cards(p1_cards)

    print("玩家手牌：", str(player.hand))
    print("玩家是否要当地主：", player.decide_landlord(bottom))