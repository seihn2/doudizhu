"""
游戏数据模型
定义游戏房间、玩家信息等数据结构
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from fastapi import WebSocket
from enum import Enum


class RoomStatus(Enum):
    """房间状态枚举"""
    WAITING = "waiting"      # 等待玩家
    PLAYING = "playing"      # 游戏中
    FINISHED = "finished"    # 游戏结束


@dataclass
class PlayerInfo:
    """玩家信息"""
    player_id: int
    name: str
    websocket: WebSocket
    is_connected: bool = True

    def __hash__(self):
        return hash(self.player_id)


@dataclass
class GameRoom:
    """游戏房间"""
    room_id: str
    room_name: str
    players: List[PlayerInfo] = field(default_factory=list)
    status: str = "waiting"
    game_controller = None
    created_at: float = field(default_factory=lambda: __import__('time').time())
    max_players: int = 3

    def add_player(self, player_info: PlayerInfo) -> bool:
        """添加玩家到房间"""
        if len(self.players) >= self.max_players:
            return False

        # 检查是否已存在同名玩家
        for player in self.players:
            if player.name == player_info.name:
                return False

        self.players.append(player_info)
        return True

    def remove_player(self, player_name: str) -> bool:
        """从房间移除玩家"""
        for i, player in enumerate(self.players):
            if player.name == player_name:
                self.players.pop(i)
                return True
        return False

    def get_player(self, player_name: str) -> Optional[PlayerInfo]:
        """根据名称获取玩家"""
        for player in self.players:
            if player.name == player_name:
                return player
        return None

    def is_full(self) -> bool:
        """检查房间是否已满"""
        return len(self.players) >= self.max_players

    def get_player_names(self) -> List[str]:
        """获取所有玩家名称"""
        return [player.name for player in self.players]


@dataclass
class GameMessage:
    """游戏消息"""
    type: str
    data: Dict[str, Any] = field(default_factory=dict)
    sender: Optional[str] = None
    timestamp: float = field(default_factory=lambda: __import__('time').time())


@dataclass
class CardData:
    """卡牌数据"""
    value: int
    suit: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "suit": self.suit
        }


@dataclass
class PlayCardsAction:
    """出牌动作"""
    player_name: str
    cards: List[CardData]
    card_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "player_name": self.player_name,
            "cards": [card.to_dict() for card in self.cards],
            "card_type": self.card_type
        }


@dataclass
class GameStateData:
    """游戏状态数据"""
    phase: str
    current_player_idx: int
    landlord_idx: Optional[int]
    players_card_count: List[int]
    last_play: Optional[Dict[str, Any]]
    round_count: int
    pass_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase,
            "current_player_idx": self.current_player_idx,
            "landlord_idx": self.landlord_idx,
            "players_card_count": self.players_card_count,
            "last_play": self.last_play,
            "round_count": self.round_count,
            "pass_count": self.pass_count
        }