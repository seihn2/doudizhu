"""
演示修复后的LLM AI出牌功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game.cards import create_cards_from_values
from game.rules import RuleEngine
from ai.llm_player import LLMPlayer, LLMConfig


def demo_fixed_llm():
    """演示修复后的LLM功能"""
    print("=== 斗地主LLM AI修复演示 ===")

    # 创建测试配置
    config = LLMConfig(
        provider="test",
        api_key="test",
        model="test"
    )

    player = LLMPlayer("智能AI", 0, config)

    # 模拟手牌
    test_cards = create_cards_from_values([3, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
    player.hand.cards = test_cards
    player.is_landlord = True

    print(f"AI手牌: {sorted([card.value for card in player.hand.cards])}")

    # 模拟各种LLM响应
    scenarios = [
        {
            "description": "正确的对子出牌",
            "response": '{"action": "play_cards", "cards": [3, 3], "card_type": "对子", "reasoning": "出小对子", "confidence": 0.8}',
            "expected": "对子 - [3, 3]"
        },
        {
            "description": "错误的牌型（假对子）",
            "response": '{"action": "play_cards", "cards": [3, 4], "card_type": "对子", "reasoning": "错误的对子", "confidence": 0.8}',
            "expected": "过牌（无效牌型）"
        },
        {
            "description": "不存在的牌",
            "response": '{"action": "play_cards", "cards": [15, 16], "card_type": "对子", "reasoning": "大对子", "confidence": 0.8}',
            "expected": "过牌（牌不存在）"
        },
        {
            "description": "合法的顺子",
            "response": '{"action": "play_cards", "cards": [5, 6, 7, 8, 9], "card_type": "顺子", "reasoning": "出顺子", "confidence": 0.9}',
            "expected": "顺子 - [5, 6, 7, 8, 9]"
        },
        {
            "description": "主动选择过牌",
            "response": '{"action": "pass", "reasoning": "等待时机", "confidence": 0.7}',
            "expected": "过牌"
        }
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n场景 {i}: {scenario['description']}")
        print(f"LLM响应: {scenario['response'][:50]}...")

        # 模拟解析过程
        result = player._parse_play_response(scenario['response'])

        if result is None:
            actual = "过牌"
        else:
            pattern = RuleEngine.analyze_cards(result)
            type_name = RuleEngine.get_card_type_name(pattern.card_type)
            card_values = [card.value for card in result]
            actual = f"{type_name} - {card_values}"

        print(f"期望结果: {scenario['expected']}")
        print(f"实际结果: {actual}")
        print(f"测试结果: {'通过' if scenario['expected'] in actual or actual in scenario['expected'] else '失败'}")


def show_improvement_summary():
    """显示改进总结"""
    print("\n=== 修复总结 ===")

    improvements = [
        "增强了prompt中的规则描述，包含详细的牌型规则",
        "添加了跟牌要求的明确说明",
        "实现了牌值验证，检查牌值范围和数量",
        "增强了牌值转换逻辑，避免重复选择同一张牌",
        "添加了牌型合法性验证",
        "实现了跟牌规则验证",
        "增加了详细的错误处理和调试信息",
        "保留了备用策略机制，API失败时降级到算法AI"
    ]

    for improvement in improvements:
        print(improvement)

    print("\n=== 解决的问题 ===")
    problems_solved = [
        "LLM出不存在的牌 -> 现在会验证牌是否在手牌中",
        "LLM出无效牌型 -> 现在会验证牌型是否合法",
        "LLM违反跟牌规则 -> 现在会检查是否能跟上一手牌",
        "重复使用同一张牌 -> 修复了牌值转换逻辑",
        "缺少错误处理 -> 增加了全面的验证和降级机制"
    ]

    for problem in problems_solved:
        print(problem)


if __name__ == "__main__":
    try:
        demo_fixed_llm()
        show_improvement_summary()

        print("\n=== 使用建议 ===")
        print("1. 确保LLM API配置正确")
        print("2. 调整prompt温度参数以获得更稳定的输出")
        print("3. 监控AI决策日志，必要时进一步优化prompt")
        print("4. 在生产环境中测试各种边缘情况")

    except Exception as e:
        print(f"演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()