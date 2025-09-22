"""
WebSocket连接管理器
管理WebSocket连接和消息广播
"""

from fastapi import WebSocket
from typing import Dict, List, Set
import json
import asyncio
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 存储房间的连接 {room_id: {websocket: player_name}}
        self.room_connections: Dict[str, Dict[WebSocket, str]] = {}
        # 存储玩家的连接 {player_name: websocket}
        self.player_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, room_id: str, player_name: str):
        """建立WebSocket连接"""
        await websocket.accept()

        # 添加到房间连接
        if room_id not in self.room_connections:
            self.room_connections[room_id] = {}
        self.room_connections[room_id][websocket] = player_name

        # 添加到玩家连接
        self.player_connections[player_name] = websocket

        logger.info(f"玩家 {player_name} 连接到房间 {room_id}")

    def disconnect(self, websocket: WebSocket, room_id: str):
        """断开WebSocket连接"""
        player_name = None

        # 从房间连接中移除
        if room_id in self.room_connections:
            if websocket in self.room_connections[room_id]:
                player_name = self.room_connections[room_id][websocket]
                del self.room_connections[room_id][websocket]

                # 如果房间没有连接了，删除房间
                if not self.room_connections[room_id]:
                    del self.room_connections[room_id]

        # 从玩家连接中移除
        if player_name and player_name in self.player_connections:
            del self.player_connections[player_name]

        if player_name:
            logger.info(f"玩家 {player_name} 从房间 {room_id} 断开连接")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送个人消息"""
        try:
            await websocket.send_text(json.dumps(message, ensure_ascii=False))
        except Exception as e:
            logger.error(f"发送个人消息失败: {e}")

    async def send_to_player(self, message: dict, player_name: str):
        """发送消息给指定玩家"""
        if player_name in self.player_connections:
            websocket = self.player_connections[player_name]
            await self.send_personal_message(message, websocket)

    async def broadcast_to_room(self, room_id: str, message: dict):
        """向房间内所有连接广播消息"""
        if room_id not in self.room_connections:
            return

        disconnected_connections = []

        for websocket, player_name in self.room_connections[room_id].items():
            try:
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.error(f"向玩家 {player_name} 广播消息失败: {e}")
                disconnected_connections.append(websocket)

        # 清理断开的连接
        for websocket in disconnected_connections:
            self.disconnect(websocket, room_id)

    async def broadcast_to_all(self, message: dict):
        """向所有连接广播消息"""
        for room_id in self.room_connections:
            await self.broadcast_to_room(room_id, message)

    def get_room_players(self, room_id: str) -> List[str]:
        """获取房间内的玩家列表"""
        if room_id not in self.room_connections:
            return []
        return list(self.room_connections[room_id].values())

    def get_player_count(self, room_id: str) -> int:
        """获取房间内的玩家数量"""
        if room_id not in self.room_connections:
            return 0
        return len(self.room_connections[room_id])

    def is_player_connected(self, player_name: str) -> bool:
        """检查玩家是否在线"""
        return player_name in self.player_connections

    def get_all_rooms(self) -> List[str]:
        """获取所有房间ID列表"""
        return list(self.room_connections.keys())

    async def cleanup_disconnected(self):
        """清理断开的连接"""
        disconnected_players = []

        for player_name, websocket in self.player_connections.items():
            try:
                # 尝试发送ping来检查连接状态
                await websocket.ping()
            except Exception:
                disconnected_players.append(player_name)

        # 清理断开的玩家
        for player_name in disconnected_players:
            websocket = self.player_connections[player_name]
            # 找到玩家所在的房间并断开连接
            for room_id, connections in self.room_connections.items():
                if websocket in connections:
                    self.disconnect(websocket, room_id)
                    break

    async def periodic_cleanup(self, interval: int = 30):
        """定期清理断开的连接"""
        while True:
            await asyncio.sleep(interval)
            await self.cleanup_disconnected()


# 全局连接管理器实例
connection_manager = ConnectionManager()


class WebSocketHandler:
    """WebSocket消息处理器"""

    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager

    async def handle_message(self, websocket: WebSocket, room_id: str,
                           player_name: str, message: dict):
        """处理WebSocket消息"""
        message_type = message.get("type")

        if message_type == "ping":
            # 心跳消息
            await self.connection_manager.send_personal_message(
                {"type": "pong"}, websocket
            )

        elif message_type == "chat":
            # 聊天消息
            chat_message = {
                "type": "chat",
                "player_name": player_name,
                "message": message.get("message", ""),
                "timestamp": __import__('time').time()
            }
            await self.connection_manager.broadcast_to_room(room_id, chat_message)

        elif message_type == "game_action":
            # 游戏动作消息
            action_data = {
                "type": "game_action",
                "player_name": player_name,
                "action": message.get("action"),
                "data": message.get("data", {})
            }
            await self.connection_manager.broadcast_to_room(room_id, action_data)

        else:
            logger.warning(f"未知消息类型: {message_type}")


# 创建消息处理器实例
websocket_handler = WebSocketHandler(connection_manager)