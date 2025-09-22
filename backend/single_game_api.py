"""
单人游戏API
提供简化的单人游戏后端支持，集成现有的AI玩家逻辑
"""

import sys
import os
import json
from typing import Dict, List, Optional, Any

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.game_state import GameController, GamePhase
from game.player import Player
from game.cards import Card
from ai.ai_player import AIPlayer


class WebPlayer(Player):
    """Web玩家类，用于单人游戏模式"""

    def __init__(self, name: str, player_id: int):
        super().__init__(name, player_id)
        self.pending_cards = None
        self.should_pass = False

    def decide_landlord(self, bottom_cards):
        """简化的地主决策 - 总是抢地主"""
        return True

    def choose_cards_to_play(self, last_play, game_info):
        """等待前端指令"""
        if self.should_pass:
            self.should_pass = False
            return None

        if self.pending_cards:
            cards = self.pending_cards
            self.pending_cards = None
            return cards

        return None

    def set_action(self, cards=None, pass_turn=False):
        """设置玩家动作"""
        if pass_turn:
            self.should_pass = True
        else:
            self.pending_cards = cards


class SingleGameManager:
    """单人游戏管理器"""

    def __init__(self):
        self.games: Dict[str, Dict] = {}

    def create_game(self, game_id: str, player_name: str) -> Dict[str, Any]:
        """创建新游戏"""
        try:
            # 创建玩家
            human_player = WebPlayer(player_name, 0)
            ai_player_1 = AIPlayer("AI玩家1", 1)
            ai_player_2 = AIPlayer("AI玩家2", 2)

            players = [human_player, ai_player_1, ai_player_2]

            # 创建游戏控制器
            controller = GameController()
            controller.start_game(players)

            # 叫地主阶段
            if not controller.bidding_phase():
                # 如果没人要当地主，随机分配
                import random
                controller.state.set_landlord(random.randint(0, 2))
                controller.state.phase = GamePhase.PLAYING

            # 保存游戏状态
            self.games[game_id] = {
                'controller': controller,
                'human_player': human_player,
                'ai_players': [ai_player_1, ai_player_2],
                'last_action_time': __import__('time').time(),
                'play_history': []  # 保存最近3次出牌记录
            }

            return self.get_game_state(game_id)

        except Exception as e:
            print(f"创建游戏失败: {e}")
            return {'error': str(e)}

    def get_game_state(self, game_id: str) -> Dict[str, Any]:
        """获取游戏状态"""
        if game_id not in self.games:
            return {'error': '游戏不存在'}

        try:
            game = self.games[game_id]
            controller = game['controller']
            human_player = game['human_player']

            # 获取玩家手牌
            player_cards = [
                {
                    'value': card.value,
                    'suit': card.suit.value if card.suit else None
                }
                for card in human_player.get_hand_cards()
            ]

            # 获取游戏信息
            game_info = controller.state.get_game_info()

            # 获取最后出牌信息
            last_play_info = None
            if controller.state.last_play:
                last_play_info = {
                    'cards': [
                        {
                            'value': card.value,
                            'suit': card.suit.value if card.suit else None
                        }
                        for card in controller.state.last_play.cards
                    ],
                    'card_type': controller.state.last_play.card_type.value,
                    'player_idx': controller.state.last_player_idx,
                    'player_name': controller.state.players[controller.state.last_player_idx].name
                }

            return {
                'game_info': game_info,
                'player_cards': player_cards,
                'last_play': last_play_info,
                'play_history': game['play_history'],  # 添加出牌历史
                'players': [
                    {
                        'name': player.name,
                        'card_count': len(player.hand.cards),
                        'is_landlord': player.is_landlord,
                        'score': player.score
                    }
                    for player in controller.state.players
                ],
                'is_game_over': controller.is_game_over(),
                'winner': controller.get_winner().name if controller.get_winner() else None
            }

        except Exception as e:
            print(f"获取游戏状态失败: {e}")
            return {'error': str(e)}

    def play_cards(self, game_id: str, cards_data: List[Dict]) -> Dict[str, Any]:
        """玩家出牌"""
        if game_id not in self.games:
            return {'error': '游戏不存在'}

        try:
            game = self.games[game_id]
            controller = game['controller']
            human_player = game['human_player']

            # 检查是否轮到玩家
            if controller.state.current_player_idx != 0:
                return {'error': '不是你的回合'}

            # 转换卡牌数据
            from game.cards import Card, Suit
            cards = []
            for card_data in cards_data:
                suit = None
                if card_data.get('suit'):
                    suit = Suit(card_data['suit'])
                cards.append(Card(card_data['value'], suit))

            # 设置玩家动作
            human_player.set_action(cards=cards)

            # 执行回合
            success = controller.play_turn()

            if not success:
                return {'error': '出牌失败，请检查牌型'}

            # 记录出牌历史
            self._add_play_history(game_id, 0, cards_data, '玩家出牌')

            # 执行AI回合
            self._execute_ai_turns(game_id)

            return self.get_game_state(game_id)

        except Exception as e:
            print(f"出牌失败: {e}")
            return {'error': str(e)}

    def pass_turn(self, game_id: str) -> Dict[str, Any]:
        """玩家过牌"""
        if game_id not in self.games:
            return {'error': '游戏不存在'}

        try:
            game = self.games[game_id]
            controller = game['controller']
            human_player = game['human_player']

            # 检查是否轮到玩家
            if controller.state.current_player_idx != 0:
                return {'error': '不是你的回合'}

            # 设置过牌动作
            human_player.set_action(pass_turn=True)

            # 执行回合
            controller.play_turn()

            # 记录过牌历史
            self._add_play_history(game_id, 0, [], '玩家过牌')

            # 执行AI回合
            self._execute_ai_turns(game_id)

            return self.get_game_state(game_id)

        except Exception as e:
            print(f"过牌失败: {e}")
            return {'error': str(e)}

    def _execute_ai_turns(self, game_id: str):
        """执行AI回合"""
        if game_id not in self.games:
            return

        game = self.games[game_id]
        controller = game['controller']

        # 执行AI回合直到轮到玩家或游戏结束
        max_ai_turns = 10  # 防止无限循环
        ai_turn_count = 0

        while (controller.state.current_player_idx != 0 and
               not controller.is_game_over() and
               ai_turn_count < max_ai_turns):

            current_ai_idx = controller.state.current_player_idx
            ai_player_name = controller.state.players[current_ai_idx].name

            success = controller.play_turn()
            if not success:
                break

            # 记录AI动作历史
            if controller.state.last_play and controller.state.last_player_idx == current_ai_idx:
                # AI出牌了
                ai_cards = [
                    {'value': card.value, 'suit': card.suit.value if card.suit else None}
                    for card in controller.state.last_play.cards
                ]
                self._add_play_history(game_id, current_ai_idx, ai_cards, f'{ai_player_name}出牌')
            else:
                # AI过牌了
                self._add_play_history(game_id, current_ai_idx, [], f'{ai_player_name}过牌')

            ai_turn_count += 1

    def _add_play_history(self, game_id: str, player_idx: int, cards: List[Dict], action_type: str):
        """添加出牌历史记录"""
        if game_id not in self.games:
            return

        game = self.games[game_id]
        controller = game['controller']
        player_name = controller.state.players[player_idx].name

        # 创建历史记录
        history_entry = {
            'player_idx': player_idx,
            'player_name': player_name,
            'action_type': action_type,
            'cards': cards,
            'timestamp': __import__('time').time()
        }

        # 添加到历史记录
        game['play_history'].append(history_entry)

        # 只保留最近3条记录
        if len(game['play_history']) > 3:
            game['play_history'] = game['play_history'][-3:]

    def delete_game(self, game_id: str):
        """删除游戏"""
        if game_id in self.games:
            del self.games[game_id]

    def cleanup_old_games(self, max_age_seconds: int = 3600):
        """清理旧游戏"""
        current_time = __import__('time').time()
        expired_games = []

        for game_id, game in self.games.items():
            if current_time - game['last_action_time'] > max_age_seconds:
                expired_games.append(game_id)

        for game_id in expired_games:
            self.delete_game(game_id)


# 全局游戏管理器
single_game_manager = SingleGameManager()


def get_game_manager():
    """获取游戏管理器实例"""
    return single_game_manager


if __name__ == "__main__":
    # 测试代码
    manager = SingleGameManager()

    # 创建测试游戏
    game_id = "test_game"
    result = manager.create_game(game_id, "测试玩家")

    print("游戏创建结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 获取游戏状态
    state = manager.get_game_state(game_id)
    print("\n游戏状态:")
    print(json.dumps(state, indent=2, ensure_ascii=False))