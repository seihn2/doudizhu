"""
游戏状态管理模块
管理斗地主游戏的整体状态、回合控制等
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from .cards import Card, Deck
from .player import Player
from .rules import CardPattern, RuleEngine


class GamePhase(Enum):
    """游戏阶段枚举"""
    DEALING = "dealing"          # 发牌阶段
    BIDDING = "bidding"          # 叫地主阶段
    PLAYING = "playing"          # 游戏进行阶段
    ENDED = "ended"              # 游戏结束


@dataclass
class GameState:
    """游戏状态类"""
    players: List[Player] = field(default_factory=list)
    current_player_idx: int = 0
    phase: GamePhase = GamePhase.DEALING
    landlord_idx: Optional[int] = None
    bottom_cards: List[Card] = field(default_factory=list)
    last_play: Optional[CardPattern] = None
    last_player_idx: Optional[int] = None
    pass_count: int = 0          # 连续过牌次数
    round_count: int = 0         # 回合数
    winner_idx: Optional[int] = None
    game_history: List[Dict[str, Any]] = field(default_factory=list)

    def add_player(self, player: Player):
        """添加玩家"""
        if len(self.players) < 3:
            self.players.append(player)

    def is_full(self) -> bool:
        """检查游戏是否已满3人"""
        return len(self.players) == 3

    def next_player(self):
        """切换到下一个玩家"""
        self.current_player_idx = (self.current_player_idx + 1) % 3

    def get_current_player(self) -> Player:
        """获取当前玩家"""
        return self.players[self.current_player_idx]

    def get_landlord(self) -> Optional[Player]:
        """获取地主玩家"""
        if self.landlord_idx is not None:
            return self.players[self.landlord_idx]
        return None

    def set_landlord(self, player_idx: int):
        """设置地主"""
        self.landlord_idx = player_idx
        for i, player in enumerate(self.players):
            player.set_landlord(i == player_idx)

    def reset_pass_count(self):
        """重置过牌计数"""
        self.pass_count = 0

    def increment_pass_count(self):
        """增加过牌计数"""
        self.pass_count += 1

    def should_clear_last_play(self) -> bool:
        """判断是否应该清除上一手牌（两人连续过牌）"""
        return self.pass_count >= 2

    def log_action(self, action_type: str, player_idx: int, cards: List[Card] = None, **kwargs):
        """记录游戏动作"""
        action = {
            "round": self.round_count,
            "player_idx": player_idx,
            "player_name": self.players[player_idx].name,
            "action_type": action_type,
            "cards": [{"value": card.value, "suit": card.suit.value if card.suit else None}
                     for card in (cards or [])],
            **kwargs
        }
        self.game_history.append(action)

    def get_game_info(self) -> Dict[str, Any]:
        """获取游戏信息（供AI决策使用）"""
        return {
            "phase": self.phase.value,
            "current_player_idx": self.current_player_idx,
            "landlord_idx": self.landlord_idx,
            "last_play": {
                "cards": [card.value for card in self.last_play.cards] if self.last_play else None,
                "card_type": self.last_play.card_type.value if self.last_play else None,
                "player_idx": self.last_player_idx
            },
            "players_card_count": [len(player.hand.cards) for player in self.players],
            "pass_count": self.pass_count,
            "round_count": self.round_count
        }


class GameController:
    """游戏控制器"""

    def __init__(self):
        """初始化游戏控制器"""
        self.state = GameState()
        self.deck = Deck()

    def start_game(self, players: List[Player]):
        """开始游戏"""
        if len(players) != 3:
            raise ValueError("斗地主游戏需要3个玩家")

        self.state = GameState()
        self.state.players = players
        self.deck.reset()
        self.deck.shuffle()

        # 发牌
        p1_cards, p2_cards, p3_cards, bottom_cards = self.deck.deal_cards()
        players[0].receive_cards(p1_cards)
        players[1].receive_cards(p2_cards)
        players[2].receive_cards(p3_cards)
        self.state.bottom_cards = bottom_cards

        self.state.phase = GamePhase.BIDDING
        self.state.log_action("game_start", -1)

    def bidding_phase(self) -> bool:
        """叫地主阶段"""
        if self.state.phase != GamePhase.BIDDING:
            return False

        for i in range(3):
            player = self.state.players[i]
            if player.decide_landlord(self.state.bottom_cards):
                self.state.set_landlord(i)
                # 地主获得底牌
                player.receive_cards(self.state.bottom_cards)
                self.state.current_player_idx = i
                self.state.phase = GamePhase.PLAYING
                self.state.log_action("become_landlord", i, self.state.bottom_cards)
                return True

        # 没有人要当地主，重新开始
        return False

    def play_turn(self) -> bool:
        """执行一个回合"""
        if self.state.phase != GamePhase.PLAYING:
            return False

        current_player = self.state.get_current_player()
        cards_to_play = current_player.choose_cards_to_play(
            self.state.last_play,
            self.state.get_game_info()
        )

        if cards_to_play is None:
            # 玩家选择过牌
            self.state.increment_pass_count()
            self.state.log_action("pass", self.state.current_player_idx)

            if self.state.should_clear_last_play():
                self.state.last_play = None
                self.state.last_player_idx = None
                self.state.reset_pass_count()
        else:
            # 玩家出牌
            if not current_player.hand.has_cards(cards_to_play):
                return False  # 玩家没有这些牌

            pattern = RuleEngine.analyze_cards(cards_to_play)
            if not RuleEngine.can_follow(cards_to_play, self.state.last_play):
                return False  # 无法跟上一手牌

            # 执行出牌
            current_player.play_cards(cards_to_play)
            self.state.last_play = pattern
            self.state.last_player_idx = self.state.current_player_idx
            self.state.reset_pass_count()
            self.state.log_action("play_cards", self.state.current_player_idx, cards_to_play,
                                card_type=pattern.card_type.value)

            # 检查游戏是否结束
            if current_player.is_hand_empty():
                self.state.winner_idx = self.state.current_player_idx
                self.state.phase = GamePhase.ENDED
                self.state.log_action("game_end", self.state.current_player_idx)
                return True

        # 切换到下一个玩家
        self.state.next_player()
        self.state.round_count += 1
        return True

    def is_game_over(self) -> bool:
        """检查游戏是否结束"""
        return self.state.phase == GamePhase.ENDED

    def get_winner(self) -> Optional[Player]:
        """获取获胜玩家"""
        if self.state.winner_idx is not None:
            return self.state.players[self.state.winner_idx]
        return None

    def get_game_result(self) -> Dict[str, Any]:
        """获取游戏结果"""
        if not self.is_game_over():
            return {}

        winner = self.get_winner()
        landlord = self.state.get_landlord()

        # 计算得分
        if winner == landlord:
            # 地主获胜
            result = "地主获胜"
            landlord.score += 2
            for player in self.state.players:
                if player != landlord:
                    player.score -= 1
        else:
            # 农民获胜
            result = "农民获胜"
            landlord.score -= 2
            for player in self.state.players:
                if player != landlord:
                    player.score += 1

        return {
            "result": result,
            "winner": winner.name if winner else None,
            "landlord": landlord.name if landlord else None,
            "scores": {player.name: player.score for player in self.state.players},
            "rounds": self.state.round_count,
            "history": self.state.game_history
        }

    def get_current_state_display(self) -> str:
        """获取当前游戏状态的显示文本"""
        lines = []
        lines.append(f"=== 游戏状态 ===")
        lines.append(f"阶段: {self.state.phase.value}")
        lines.append(f"回合: {self.state.round_count}")

        if self.state.landlord_idx is not None:
            landlord = self.state.get_landlord()
            lines.append(f"地主: {landlord.name}")

        lines.append(f"当前玩家: {self.state.get_current_player().name}")

        for i, player in enumerate(self.state.players):
            marker = "👑" if player.is_landlord else "👨"
            current_marker = " ← 当前" if i == self.state.current_player_idx else ""
            lines.append(f"{marker} {player.name}: {len(player.hand.cards)}张牌{current_marker}")

        if self.state.last_play:
            last_player = self.state.players[self.state.last_player_idx]
            lines.append(f"上一手牌: {last_player.name} 出了 {RuleEngine.get_card_type_name(self.state.last_play.card_type)}")

        return "\n".join(lines)


if __name__ == "__main__":
    # 测试代码
    from .player import HumanPlayer

    players = [
        HumanPlayer("玩家1", 0),
        HumanPlayer("玩家2", 1),
        HumanPlayer("玩家3", 2)
    ]

    controller = GameController()
    controller.start_game(players)

    print("游戏开始！")
    print(controller.get_current_state_display())