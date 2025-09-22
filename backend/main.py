"""
FastAPI后端主程序
提供斗地主游戏的Web API和WebSocket服务
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import asyncio
from typing import Dict, List
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.game_state import GameController, GamePhase
from game.player import Player
from ai.ai_player import AIPlayer
from websocket.connection_manager import ConnectionManager
from models.game_models import GameRoom, PlayerInfo
from single_game_api import get_game_manager

app = FastAPI(title="斗地主游戏后端", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局状态管理
connection_manager = ConnectionManager()
game_rooms: Dict[str, GameRoom] = {}
single_game_manager = get_game_manager()

@app.get("/")
async def root():
    """根路径"""
    return {"message": "斗地主游戏后端服务运行中"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "rooms": len(game_rooms)}

@app.post("/api/rooms")
async def create_room(room_name: str = "默认房间"):
    """创建游戏房间"""
    room_id = f"room_{len(game_rooms) + 1}"
    room = GameRoom(room_id=room_id, room_name=room_name)
    game_rooms[room_id] = room
    return {"room_id": room_id, "room_name": room_name}

@app.get("/api/rooms")
async def get_rooms():
    """获取所有房间列表"""
    return [
        {
            "room_id": room.room_id,
            "room_name": room.room_name,
            "player_count": len(room.players),
            "status": room.status
        }
        for room in game_rooms.values()
    ]

# 单人游戏API
@app.post("/api/single-game/create")
async def create_single_game(player_name: str):
    """创建单人游戏"""
    import uuid
    game_id = str(uuid.uuid4())[:8]
    result = single_game_manager.create_game(game_id, player_name)

    if 'error' in result:
        return {"success": False, "error": result['error']}

    return {
        "success": True,
        "game_id": game_id,
        "game_state": result
    }

@app.get("/api/single-game/{game_id}")
async def get_single_game_state(game_id: str):
    """获取单人游戏状态"""
    result = single_game_manager.get_game_state(game_id)

    if 'error' in result:
        return {"success": False, "error": result['error']}

    return {
        "success": True,
        "game_state": result
    }

@app.post("/api/single-game/{game_id}/play")
async def play_cards_single_game(game_id: str, cards: List[dict]):
    """单人游戏出牌"""
    result = single_game_manager.play_cards(game_id, cards)

    if 'error' in result:
        return {"success": False, "error": result['error']}

    return {
        "success": True,
        "game_state": result
    }

@app.post("/api/single-game/{game_id}/pass")
async def pass_turn_single_game(game_id: str):
    """单人游戏过牌"""
    result = single_game_manager.pass_turn(game_id)

    if 'error' in result:
        return {"success": False, "error": result['error']}

    return {
        "success": True,
        "game_state": result
    }

@app.websocket("/ws/{room_id}/{player_name}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, player_name: str):
    """WebSocket连接处理"""
    await connection_manager.connect(websocket, room_id, player_name)

    try:
        # 检查或创建房间
        if room_id not in game_rooms:
            game_rooms[room_id] = GameRoom(room_id=room_id, room_name=f"房间 {room_id}")

        room = game_rooms[room_id]

        # 添加玩家到房间
        if len(room.players) < 3:
            player_info = PlayerInfo(
                player_id=len(room.players),
                name=player_name,
                websocket=websocket
            )
            room.add_player(player_info)

            # 广播玩家加入消息
            await connection_manager.broadcast_to_room(room_id, {
                "type": "player_joined",
                "player_name": player_name,
                "players": [p.name for p in room.players],
                "player_count": len(room.players)
            })

            # 如果人数满3人，开始游戏
            if len(room.players) == 3:
                await start_game(room_id)

        # 处理客户端消息
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await handle_websocket_message(room_id, player_name, message)

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, room_id)
        if room_id in game_rooms:
            room = game_rooms[room_id]
            room.remove_player(player_name)

            # 广播玩家离开消息
            await connection_manager.broadcast_to_room(room_id, {
                "type": "player_left",
                "player_name": player_name,
                "players": [p.name for p in room.players],
                "player_count": len(room.players)
            })

            # 如果房间空了，删除房间
            if len(room.players) == 0:
                del game_rooms[room_id]

async def start_game(room_id: str):
    """开始游戏"""
    room = game_rooms[room_id]

    # 创建游戏玩家对象
    players = []
    for i, player_info in enumerate(room.players):
        if player_info.name.startswith("AI_"):
            player = AIPlayer(player_info.name, i)
        else:
            player = WebSocketPlayer(player_info.name, i, player_info.websocket)
        players.append(player)

    # 创建游戏控制器
    room.game_controller = GameController()
    room.game_controller.start_game(players)
    room.status = "playing"

    # 进行叫地主阶段
    if room.game_controller.bidding_phase():
        # 广播游戏开始和发牌信息
        await broadcast_game_state(room_id)

        # 开始游戏循环
        asyncio.create_task(game_loop(room_id))
    else:
        # 重新开始
        await connection_manager.broadcast_to_room(room_id, {
            "type": "game_restart",
            "message": "没有人要当地主，重新开始游戏"
        })

async def game_loop(room_id: str):
    """游戏主循环"""
    room = game_rooms[room_id]
    controller = room.game_controller

    while not controller.is_game_over():
        # 执行当前玩家回合
        success = controller.play_turn()

        if success:
            # 广播游戏状态更新
            await broadcast_game_state(room_id)
        else:
            # 处理错误
            await connection_manager.broadcast_to_room(room_id, {
                "type": "error",
                "message": "游戏执行出错"
            })
            break

        # 短暂延迟，让客户端有时间处理
        await asyncio.sleep(0.5)

    # 游戏结束，广播结果
    if controller.is_game_over():
        result = controller.get_game_result()
        await connection_manager.broadcast_to_room(room_id, {
            "type": "game_end",
            "result": result
        })

        # 重置房间状态
        room.status = "waiting"
        room.game_controller = None

async def broadcast_game_state(room_id: str):
    """广播游戏状态"""
    room = game_rooms[room_id]
    controller = room.game_controller

    game_info = controller.state.get_game_info()

    # 为每个玩家发送个性化信息
    for i, player_info in enumerate(room.players):
        player = controller.state.players[i]

        player_data = {
            "type": "game_state",
            "game_info": game_info,
            "your_cards": [{"value": card.value, "suit": card.suit.value if card.suit else None}
                          for card in player.get_hand_cards()],
            "your_index": i,
            "players": [
                {
                    "name": p.name,
                    "card_count": p.get_card_count(),
                    "is_landlord": p.is_landlord,
                    "score": p.score
                }
                for p in controller.state.players
            ]
        }

        await connection_manager.send_personal_message(player_data, player_info.websocket)

async def handle_websocket_message(room_id: str, player_name: str, message: dict):
    """处理WebSocket消息"""
    message_type = message.get("type")

    if message_type == "play_cards":
        # 处理出牌消息
        cards_data = message.get("cards", [])
        # 这里需要将卡牌数据转换为Card对象并处理出牌逻辑
        await connection_manager.broadcast_to_room(room_id, {
            "type": "cards_played",
            "player_name": player_name,
            "cards": cards_data
        })

    elif message_type == "pass":
        # 处理过牌消息
        await connection_manager.broadcast_to_room(room_id, {
            "type": "player_passed",
            "player_name": player_name
        })

    elif message_type == "chat":
        # 处理聊天消息
        await connection_manager.broadcast_to_room(room_id, {
            "type": "chat",
            "player_name": player_name,
            "message": message.get("message", "")
        })

class WebSocketPlayer(Player):
    """WebSocket玩家类"""

    def __init__(self, name: str, player_id: int, websocket: WebSocket):
        super().__init__(name, player_id)
        self.websocket = websocket
        self.pending_action = None

    def decide_landlord(self, bottom_cards):
        """决定是否要当地主（AI决策或等待用户输入）"""
        if self.name.startswith("AI_"):
            # AI玩家自动决策
            return len(self.hand.cards) >= 15  # 简单策略
        else:
            # 真实玩家，这里返回True让第一个玩家当地主（简化实现）
            return True

    def choose_cards_to_play(self, last_play, game_info):
        """选择要出的牌（AI决策或等待用户输入）"""
        if self.name.startswith("AI_"):
            # AI玩家使用AI逻辑
            from ai.ai_player import AIPlayer
            ai_player = AIPlayer(self.name, self.player_id)
            ai_player.hand = self.hand
            ai_player.is_landlord = self.is_landlord
            return ai_player.choose_cards_to_play(last_play, game_info)
        else:
            # 真实玩家，这里需要等待WebSocket消息（简化实现，暂时随机出牌）
            if last_play is None and len(self.hand.cards) > 0:
                return [self.hand.cards[0]]  # 出第一张牌
            return None  # 过牌

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )