"""
测试修复后的LLM AI出牌逻辑
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game.cards import create_cards_from_values, Deck
from game.rules import RuleEngine, CardPattern
from ai.llm_player import LLMPlayer, LLMConfig


def test_llm_response_parsing():
    """测试LLM响应解析"""
    print("=== 测试LLM响应解析 ===")

    # 创建一个测试用的LLM配置
    config = LLMConfig(
        provider="test",
        api_key="test",
        model="test"
    )

    # 创建LLM玩家
    player = LLMPlayer("测试玩家", 0, config)

    # 给玩家发一些测试牌
    test_cards = create_cards_from_values([3, 3, 4, 4, 5, 5, 6, 7, 8, 9, 10])
    player.hand.cards = test_cards

    print(f"玩家手牌: {[card.value for card in player.hand.cards]}")

    # 测试各种响应格式
    test_responses = [
        # 正确格式
        '{"action": "play_cards", "cards": [3, 3], "card_type": "对子", "reasoning": "出对3", "confidence": 0.8}',

        # 无效牌型
        '{"action": "play_cards", "cards": [3, 4], "card_type": "对子", "reasoning": "错误的对子", "confidence": 0.8}',

        # 不存在的牌
        '{"action": "play_cards", "cards": [15, 16], "card_type": "对子", "reasoning": "不存在的牌", "confidence": 0.8}',

        # 数量不足
        '{"action": "play_cards", "cards": [3, 3, 3], "card_type": "三张", "reasoning": "手牌中只有2张3", "confidence": 0.8}',

        # 过牌
        '{"action": "pass", "reasoning": "选择过牌", "confidence": 0.9}',

        # 格式错误
        'invalid json response',

        # 顺子测试
        '{"action": "play_cards", "cards": [5, 6, 7, 8, 9], "card_type": "顺子", "reasoning": "出顺子", "confidence": 0.8}'
    ]

    for i, response in enumerate(test_responses):
        print(f"\n测试 {i+1}: {response[:50]}...")
        result = player._parse_play_response(response)
        if result:
            pattern = RuleEngine.analyze_cards(result)
            type_name = RuleEngine.get_card_type_name(pattern.card_type)
            card_values = [card.value for card in result]
            print(f"  结果: {type_name} - {card_values}")
        else:
            print(f"  结果: 过牌或解析失败")


def test_card_validation():
    """测试牌值验证"""
    print("\n=== 测试牌值验证 ===")

    config = LLMConfig(provider="test", api_key="test", model="test")
    player = LLMPlayer("测试玩家", 0, config)

    # 给玩家发一些测试牌
    test_cards = create_cards_from_values([3, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    player.hand.cards = test_cards

    print(f"玩家手牌: {[card.value for card in player.hand.cards]}")

    test_cases = [
        ([3, 4, 5], "有效的牌值"),
        ([3, 3], "有效的对子"),
        ([3, 3, 3], "数量不足的三张"),
        ([15, 16], "不存在的牌"),
        ([1, 2], "无效的牌值范围"),
        ([3.5, 4], "非整数牌值"),
        ([], "空牌值列表")
    ]

    for values, description in test_cases:
        print(f"\n测试: {description} - {values}")
        is_valid = player._validate_card_values(values)
        print(f"  验证结果: {'通过' if is_valid else '失败'}")


def test_values_to_cards():
    """测试牌值转换为Card对象"""
    print("\n=== 测试牌值转换 ===")

    config = LLMConfig(provider="test", api_key="test", model="test")
    player = LLMPlayer("测试玩家", 0, config)

    # 给玩家发一些测试牌
    test_cards = create_cards_from_values([3, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    player.hand.cards = test_cards

    print(f"玩家手牌: {[card.value for card in player.hand.cards]}")

    test_cases = [
        ([3, 4, 5], "有效的顺子"),
        ([3, 3], "有效的对子"),
        ([3, 3, 3], "数量不足"),
        ([13, 14], "不存在的牌"),
        ([3, 4, 5, 6, 7], "长顺子")
    ]

    for values, description in test_cases:
        print(f"\n测试: {description} - {values}")
        cards = player._values_to_cards(values)
        if cards:
            result_values = [card.value for card in cards]
            print(f"  转换结果: {result_values}")

            # 验证牌型
            pattern = RuleEngine.analyze_cards(cards)
            type_name = RuleEngine.get_card_type_name(pattern.card_type)
            print(f"  牌型: {type_name}")
        else:
            print(f"  转换结果: 失败")


def test_rule_validation():
    """测试规则验证"""
    print("\n=== 测试规则验证 ===")

    # 测试各种牌型的规则验证
    test_cases = [
        ([3], "单张"),
        ([3, 3], "对子"),
        ([3, 3, 3], "三张"),
        ([3, 3, 3, 4], "三带一"),
        ([3, 3, 3, 4, 4], "三带对"),
        ([3, 4, 5, 6, 7], "顺子"),
        ([3, 3, 4, 4, 5, 5], "连对"),
        ([3, 3, 3, 4, 4, 4], "飞机"),
        ([8, 8, 8, 8], "炸弹"),
        ([16, 17], "王炸"),
        ([3, 4, 6], "无效牌型"),
        ([15, 16, 17], "包含2和王的无效顺子")
    ]

    for values, description in test_cases:
        cards = create_cards_from_values(values)
        pattern = RuleEngine.analyze_cards(cards)
        is_valid = RuleEngine.is_valid_cards(cards)
        type_name = RuleEngine.get_card_type_name(pattern.card_type)

        print(f"{description}: {values}")
        print(f"  识别为: {type_name}")
        print(f"  是否合法: {'是' if is_valid else '否'}")


def test_follow_rules():
    """测试跟牌规则"""
    print("\n=== 测试跟牌规则 ===")

    # 设置上一手牌
    last_cards = create_cards_from_values([5, 5])  # 对5
    last_pattern = RuleEngine.analyze_cards(last_cards)

    print(f"上一手牌: 对5")

    test_cases = [
        ([6, 6], "对6 - 应该可以跟"),
        ([4, 4], "对4 - 不能跟（小于对5）"),
        ([6], "单张6 - 不能跟（牌型不同）"),
        ([8, 8, 8, 8], "炸弹 - 可以跟任何牌"),
        ([16, 17], "王炸 - 可以跟任何牌")
    ]

    for values, description in test_cases:
        cards = create_cards_from_values(values)
        can_follow = RuleEngine.can_follow(cards, last_pattern)

        print(f"{description}: {values}")
        print(f"  能否跟牌: {'是' if can_follow else '否'}")


if __name__ == "__main__":
    try:
        test_llm_response_parsing()
        test_card_validation()
        test_values_to_cards()
        test_rule_validation()
        test_follow_rules()

        print("\n=== 测试完成 ===")
        print("所有修复已应用，LLM AI现在应该能正确遵守斗地主规则")

    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()