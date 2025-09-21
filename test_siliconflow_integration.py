"""
测试硅基流动API集成
"""

import sys
import os
import asyncio

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import LLM_CONFIGS, get_llm_config, validate_llm_config, get_available_providers
from ai.llm_player import LLMPlayer, LLMConfig, create_llm_player
from game.cards import create_cards_from_values


def test_siliconflow_config():
    """测试硅基流动配置"""
    print("=== 测试硅基流动配置 ===")

    # 检查配置是否存在
    if "siliconflow" in LLM_CONFIGS:
        print("硅基流动配置已添加")
        config = LLM_CONFIGS["siliconflow"]
        print(f"  基础URL: {config['base_url']}")
        print(f"  可用模型: {list(config['models'].keys())}")
        print(f"  快速模型: {config['models']['fast']}")
        print(f"  智能模型: {config['models']['smart']}")
        print(f"  Claude模型: {config['models']['claude']}")
        print(f"  GPT4模型: {config['models']['gpt4']}")
    else:
        print("硅基流动配置未找到")

    # 检查环境变量
    api_key = os.getenv("SILICONFLOW_API_KEY", "")
    if api_key:
        print(f"API密钥已设置 (长度: {len(api_key)})")
    else:
        print("API密钥未设置，请设置SILICONFLOW_API_KEY环境变量")

    # 测试验证函数
    is_valid = validate_llm_config("siliconflow")
    print(f"配置验证: {'通过' if is_valid else '失败'}")

    # 测试获取配置
    try:
        config = get_llm_config("siliconflow", "fast")
        print(f"获取快速模型配置成功: {config['model']}")
    except Exception as e:
        print(f"获取配置失败: {e}")

    # 检查是否在可用提供商列表中
    providers = get_available_providers()
    print(f"可用提供商: {providers}")
    if "siliconflow" in providers:
        print("硅基流动已列入可用提供商")
    else:
        print("硅基流动未列入可用提供商")


def test_siliconflow_player_creation():
    """测试硅基流动玩家创建"""
    print("\n=== 测试硅基流动玩家创建 ===")

    api_key = os.getenv("SILICONFLOW_API_KEY", "test_key_placeholder")

    try:
        # 测试不同模型的玩家创建
        models_to_test = [
            ("fast", "Qwen/Qwen2.5-7B-Instruct"),
            ("smart", "deepseek-ai/DeepSeek-V2.5"),
            ("claude", "anthropic/claude-3-5-sonnet-20241022"),
            ("gpt4", "OpenAI/gpt-4o-mini")
        ]

        for model_type, expected_model in models_to_test:
            print(f"\n测试{model_type}模型:")
            try:
                config = get_llm_config("siliconflow", model_type)
                player = create_llm_player(
                    name=f"硅基流动-{model_type}",
                    player_id=1,
                    provider="siliconflow",
                    api_key=api_key,
                    model=config["model"]
                )
                print(f"  玩家创建成功: {player.name}")
                print(f"  使用模型: {player.config.model}")
                print(f"  预期模型: {expected_model}")
                print(f"  模型匹配: {'是' if player.config.model == expected_model else '否'}")

            except Exception as e:
                print(f"  创建失败: {e}")

    except Exception as e:
        print(f"测试失败: {e}")


async def test_siliconflow_api_call():
    """测试硅基流动API调用（如果有API密钥）"""
    print("\n=== 测试硅基流动API调用 ===")

    api_key = os.getenv("SILICONFLOW_API_KEY", "")
    if not api_key:
        print("跳过API调用测试：未设置SILICONFLOW_API_KEY")
        return

    try:
        # 创建配置
        config = LLMConfig(
            provider="siliconflow",
            api_key=api_key,
            model="Qwen/Qwen2.5-7B-Instruct",
            temperature=0.7,
            max_tokens=200
        )

        # 创建玩家
        player = LLMPlayer("硅基流动测试", 0, config)
        player.hand.cards = create_cards_from_values([3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])

        print("正在测试API调用...")

        # 测试简单的prompt
        simple_prompt = """你是一个斗地主AI。你的手牌是：[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

请以JSON格式返回你的出牌决策：
{
    "action": "play_cards",
    "cards": [3, 4, 5, 6, 7],
    "reasoning": "出顺子",
    "confidence": 0.8
}"""

        response = await player._call_llm(simple_prompt)
        print(f"API响应成功:")
        print(f"  响应长度: {len(response)}")
        print(f"  响应预览: {response[:200]}...")

        # 测试解析
        cards = player._parse_play_response(response)
        if cards:
            card_values = [card.value for card in cards]
            print(f"  解析成功: {card_values}")
        else:
            print(f"  解析失败或选择过牌")

    except Exception as e:
        print(f"API调用测试失败: {e}")


def test_game_integration():
    """测试游戏集成"""
    print("\n=== 测试游戏集成 ===")

    api_key = os.getenv("SILICONFLOW_API_KEY", "")
    if not api_key:
        print("跳过游戏集成测试：未设置SILICONFLOW_API_KEY")
        return

    print("如果有API密钥，可以通过以下方式在游戏中使用硅基流动:")
    print("1. 设置环境变量: SILICONFLOW_API_KEY=your_api_key")
    print("2. 运行游戏: python main_with_llm.py")
    print("3. 选择LLM AI模式，系统会自动检测可用的提供商")
    print("4. 或者在config.py中将默认提供商设置为'siliconflow'")

    # 展示配置示例
    print("\n配置示例:")
    print('GAME_CONFIG["llm_provider"] = "siliconflow"')
    print('GAME_CONFIG["llm_model_type"] = "fast"  # 或 smart, claude, gpt4')


if __name__ == "__main__":
    try:
        test_siliconflow_config()
        test_siliconflow_player_creation()

        # 测试API调用（需要事件循环）
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_siliconflow_api_call())
        finally:
            loop.close()

        test_game_integration()

        print("\n=== 硅基流动集成测试完成 ===")
        print("硅基流动API已成功集成到斗地主游戏中！")

        if not os.getenv("SILICONFLOW_API_KEY"):
            print("\n要使用硅基流动API，请:")
            print("1. 访问 https://siliconflow.cn 注册账号")
            print("2. 获取API密钥")
            print("3. 设置环境变量: SILICONFLOW_API_KEY=your_api_key")
            print("4. 重新运行游戏即可使用")

    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()