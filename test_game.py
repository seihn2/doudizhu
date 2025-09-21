"""
简单的游戏测试脚本
用于验证核心功能是否正常工作
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game.cards import Deck, create_cards_from_values
from game.rules import RuleEngine, CardType
from game.player import HumanPlayer
from game.game_state import GameController
from ai.ai_player import AIPlayerFactory, Difficulty


def test_basic_functionality():
    """测试基础功能"""
    print("=== 测试基础功能 ===")

    # 测试牌型识别
    print("\n1. 测试牌型识别:")
    test_cases = [
        ([3], "单张"),
        ([3, 3], "对子"),
        ([3, 3, 3], "三张"),
        ([3, 3, 3, 4], "三带一"),
        ([3, 4, 5, 6, 7], "顺子"),
        ([8, 8, 8, 8], "炸弹"),
        ([16, 17], "王炸"),
    ]

    for values, expected in test_cases:
        cards = create_cards_from_values(values)
        pattern = RuleEngine.analyze_cards(cards)
        type_name = RuleEngine.get_card_type_name(pattern.card_type)
        print(f"  {values} -> {type_name} (期望: {expected})")
        assert type_name != "无效牌型", f"牌型识别失败: {values}"

    print("  [OK] 牌型识别测试通过")

    # 测试发牌
    print("\n2. 测试发牌:")
    deck = Deck()
    deck.shuffle()
    p1_cards, p2_cards, p3_cards, bottom_cards = deck.deal_cards()

    print(f"  玩家1: {len(p1_cards)}张")
    print(f"  玩家2: {len(p2_cards)}张")
    print(f"  玩家3: {len(p3_cards)}张")
    print(f"  底牌: {len(bottom_cards)}张")

    total = len(p1_cards) + len(p2_cards) + len(p3_cards) + len(bottom_cards)
    assert total == 54, f"总牌数错误: {total}"
    print("  [OK] 发牌测试通过")

    # 测试AI创建
    print("\n3. 测试AI创建:")
    ai_players = AIPlayerFactory.create_ai_team(Difficulty.MEDIUM)
    print(f"  创建了{len(ai_players)}个AI玩家")
    for ai in ai_players:
        print(f"  - {ai.name} (难度: {ai.difficulty.value})")
    print("  [OK] AI创建测试通过")


def test_game_flow():
    """测试游戏流程"""
    print("\n=== 测试游戏流程 ===")

    # 创建玩家
    human_player = HumanPlayer("测试玩家", 0)
    ai_players = AIPlayerFactory.create_ai_team(Difficulty.EASY)
    players = [human_player] + ai_players

    # 创建游戏控制器
    controller = GameController()
    controller.start_game(players)

    print(f"游戏阶段: {controller.state.phase.value}")
    print(f"玩家数量: {len(controller.state.players)}")

    # 显示手牌信息
    for i, player in enumerate(players):
        cards_count = len(player.get_hand_cards())
        print(f"玩家{i+1} ({player.name}): {cards_count}张牌")

    print("底牌数量:", len(controller.state.bottom_cards))
    print("[OK] 游戏初始化测试通过")


def test_card_comparison():
    """测试牌型比较"""
    print("\n=== 测试牌型比较 ===")

    # 测试基本比较
    cards1 = create_cards_from_values([7])
    cards2 = create_cards_from_values([8])

    pattern1 = RuleEngine.analyze_cards(cards1)
    pattern2 = RuleEngine.analyze_cards(cards2)

    assert pattern2.is_greater_than(pattern1), "8应该比7大"
    assert not pattern1.is_greater_than(pattern2), "7不应该比8大"
    print("[OK] 基本牌型比较测试通过")

    # 测试炸弹vs普通牌
    bomb_cards = create_cards_from_values([3, 3, 3, 3])
    normal_cards = create_cards_from_values([14, 14, 14])  # 三个A

    bomb_pattern = RuleEngine.analyze_cards(bomb_cards)
    normal_pattern = RuleEngine.analyze_cards(normal_cards)

    assert bomb_pattern.is_greater_than(normal_pattern), "炸弹应该比普通牌大"
    print("[OK] 炸弹vs普通牌测试通过")

    # 测试王炸vs炸弹
    rocket_cards = create_cards_from_values([16, 17])
    rocket_pattern = RuleEngine.analyze_cards(rocket_cards)

    assert rocket_pattern.is_greater_than(bomb_pattern), "王炸应该比炸弹大"
    print("[OK] 王炸vs炸弹测试通过")


if __name__ == "__main__":
    print("开始游戏功能测试...")

    try:
        test_basic_functionality()
        test_game_flow()
        test_card_comparison()

        print("\n" + "="*50)
        print("所有测试通过！游戏功能正常。")
        print("现在可以运行 python main.py 开始游戏")
        print("="*50)

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()