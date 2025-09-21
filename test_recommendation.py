"""
测试推荐系统
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game.cards import create_cards_from_values
from game.rules import RuleEngine
from ai.card_recommender import CardRecommender


def test_recommendation_system():
    """测试推荐系统功能"""
    print("=== 测试出牌推荐系统 ===")

    # 创建测试手牌
    test_cards = create_cards_from_values([3, 4, 5, 6, 7, 8, 8, 8, 11, 11, 14, 15, 16, 17])

    recommender = CardRecommender()

    print("测试手牌:", [card.value for card in test_cards])
    print()

    print("=== 主动出牌推荐 ===")
    recs = recommender.get_recommendations(test_cards)
    for i, rec in enumerate(recs, 1):
        print(f"{i}. {recommender.format_recommendation(rec)}")

    print("\n=== 跟单张7的推荐 ===")
    last_cards = create_cards_from_values([7])
    last_pattern = RuleEngine.analyze_cards(last_cards)

    recs = recommender.get_recommendations(test_cards, last_pattern)
    for i, rec in enumerate(recs, 1):
        print(f"{i}. {recommender.format_recommendation(rec)}")

    print("\n=== 跟对子K的推荐 ===")
    last_cards = create_cards_from_values([13, 13])
    last_pattern = RuleEngine.analyze_cards(last_cards)

    recs = recommender.get_recommendations(test_cards, last_pattern)
    for i, rec in enumerate(recs, 1):
        print(f"{i}. {recommender.format_recommendation(rec)}")

    print("\n[OK] 推荐系统测试完成！")


def test_invalid_card_handling():
    """测试无效牌型处理"""
    print("\n=== 测试无效牌型处理 ===")

    # 测试无效牌型
    invalid_cases = [
        [3, 5, 7],          # 无效的三张不同牌
        [3, 4, 6, 7],       # 无效的不连续牌
        [3, 3, 4, 5, 6],    # 无效的混合牌型
    ]

    for case in invalid_cases:
        cards = create_cards_from_values(case)
        pattern = RuleEngine.analyze_cards(cards)
        is_valid = pattern.card_type.value != "invalid"
        print(f"牌型 {case}: {'有效' if is_valid else '无效'}")

    print("[OK] 无效牌型处理测试完成！")


if __name__ == "__main__":
    try:
        test_recommendation_system()
        test_invalid_card_handling()
        print("\n" + "="*50)
        print("所有增强功能测试通过！")
        print("="*50)
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()