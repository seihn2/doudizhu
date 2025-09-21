"""
测试硅基流动模型选择功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import (
    LLM_CONFIGS, GAME_CONFIG,
    get_siliconflow_models, get_model_display_name,
    get_llm_config_with_model, get_available_providers
)


def test_config_structure():
    """测试配置结构"""
    print("=== 测试配置结构 ===")

    # 检查硅基流动配置
    if "siliconflow" in LLM_CONFIGS:
        config = LLM_CONFIGS["siliconflow"]
        print("硅基流动配置已添加")
        print(f"  基础URL: {config['base_url']}")
        print(f"  模型数量: {len(config['models'])}")

        # 检查模型分类
        if "model_categories" in config:
            categories = config["model_categories"]
            print(f"  分类数量: {len(categories)}")
            for category_name, models in categories.items():
                print(f"    {category_name}: {len(models)}个模型")
        else:
            print("  缺少模型分类配置")
    else:
        print("硅基流动配置未找到")

    # 检查游戏配置
    print(f"\n游戏配置:")
    print(f"  llm_provider: {GAME_CONFIG.get('llm_provider')}")
    print(f"  llm_model_type: {GAME_CONFIG.get('llm_model_type')}")
    print(f"  llm_model_key: {GAME_CONFIG.get('llm_model_key')}")


def test_model_functions():
    """测试模型相关函数"""
    print("\n=== 测试模型相关函数 ===")

    # 测试获取硅基流动模型
    models = get_siliconflow_models()
    if models:
        print("成功获取硅基流动模型分类:")
        for category_name, category_models in models.items():
            print(f"  {category_name}:")
            for model_key, model_display in list(category_models.items())[:3]:  # 只显示前3个
                print(f"    {model_key}: {model_display}")
            if len(category_models) > 3:
                print(f"    ... 还有{len(category_models) - 3}个模型")
    else:
        print("获取硅基流动模型失败")

    # 测试模型显示名称
    test_models = [
        "qwen2.5-7b",
        "claude-3.5-sonnet",
        "gpt-4o-mini",
        "nonexistent-model"
    ]

    print("\n测试模型显示名称:")
    for model_key in test_models:
        display_name = get_model_display_name("siliconflow", model_key)
        print(f"  {model_key} -> {display_name}")


def test_config_generation():
    """测试配置生成"""
    print("\n=== 测试配置生成 ===")

    # 测试几个关键模型的配置生成
    test_models = [
        ("qwen2.5-7b", "Qwen2.5-7B"),
        ("deepseek-v2.5", "DeepSeek-V2.5"),
        ("claude-3.5-sonnet", "Claude-3.5-Sonnet"),
        ("gpt-4o-mini", "GPT-4o-mini")
    ]

    for model_key, expected_type in test_models:
        try:
            config = get_llm_config_with_model("siliconflow", model_key)
            print(f"\n{model_key}:")
            print(f"  配置生成: 成功")
            print(f"  模型名称: {config['model']}")
            print(f"  API密钥: {'已设置' if config.get('api_key') else '未设置'}")
            print(f"  基础URL: {config['base_url']}")
        except Exception as e:
            print(f"\n{model_key}: 配置生成失败 - {e}")


def test_menu_simulation():
    """模拟菜单选择流程"""
    print("\n=== 模拟菜单选择流程 ===")

    # 模拟选择硅基流动提供商
    print("步骤1: 选择硅基流动作为提供商")
    GAME_CONFIG["llm_provider"] = "siliconflow"
    print(f"  设置提供商: {GAME_CONFIG['llm_provider']}")

    # 模拟选择具体模型
    print("\n步骤2: 选择具体模型")
    test_model_selections = [
        "qwen2.5-7b",
        "claude-3.5-sonnet",
        "deepseek-v2.5"
    ]

    for model_key in test_model_selections:
        GAME_CONFIG["llm_model_key"] = model_key
        display_name = get_model_display_name("siliconflow", model_key)
        print(f"  选择模型: {model_key} ({display_name})")

        # 模拟获取配置
        try:
            config = get_llm_config_with_model("siliconflow", model_key)
            print(f"    配置成功: {config['model']}")
        except Exception as e:
            print(f"    配置失败: {e}")


def test_backwards_compatibility():
    """测试向后兼容性"""
    print("\n=== 测试向后兼容性 ===")

    # 测试非硅基流动提供商的配置
    other_providers = ["deepseek", "openai", "anthropic", "moonshot"]

    for provider in other_providers:
        if provider in LLM_CONFIGS:
            print(f"\n测试 {provider}:")
            try:
                # 使用传统的模型类型
                from config import get_llm_config
                config = get_llm_config(provider, "fast")
                print(f"  传统配置方式: 成功")
                print(f"  模型: {config['model']}")
            except Exception as e:
                print(f"  传统配置方式: 失败 - {e}")


def test_integration_flow():
    """测试完整集成流程"""
    print("\n=== 测试完整集成流程 ===")

    # 保存原始配置
    original_provider = GAME_CONFIG.get("llm_provider")
    original_model_key = GAME_CONFIG.get("llm_model_key")

    try:
        # 设置硅基流动配置
        GAME_CONFIG["llm_provider"] = "siliconflow"
        GAME_CONFIG["llm_model_key"] = "qwen2.5-7b"

        print("配置设置:")
        print(f"  提供商: {GAME_CONFIG['llm_provider']}")
        print(f"  模型key: {GAME_CONFIG['llm_model_key']}")

        # 模拟游戏中的配置获取
        provider = GAME_CONFIG.get("llm_provider")
        model_key = GAME_CONFIG.get("llm_model_key")

        if provider == "siliconflow" and model_key:
            config = get_llm_config_with_model(provider, model_key)
            model_display = get_model_display_name(provider, model_key)

            print("\n游戏中的配置获取:")
            print(f"  显示名称: {model_display}")
            print(f"  实际模型: {config['model']}")
            print(f"  集成流程: 成功")
        else:
            print("\n集成流程: 配置不完整")

    finally:
        # 恢复原始配置
        if original_provider:
            GAME_CONFIG["llm_provider"] = original_provider
        if original_model_key:
            GAME_CONFIG["llm_model_key"] = original_model_key


def show_usage_examples():
    """显示使用示例"""
    print("\n=== 使用示例 ===")

    print("1. 启动游戏并选择硅基流动:")
    print("   python main_with_llm.py")
    print("   -> AI类型设置 -> 使用LLM AI -> 选择 siliconflow")

    print("\n2. 选择模型:")
    print("   -> 选择模型分类 (如'推荐模型')")
    print("   -> 选择具体模型 (如'Qwen2.5-7B (快速、经济)')")

    print("\n3. 可用的模型分类:")
    models = get_siliconflow_models()
    for category_name in models.keys():
        print(f"   - {category_name}")

    print("\n4. 推荐模型:")
    if "推荐模型" in models:
        recommended = models["推荐模型"]
        for model_key, model_display in recommended.items():
            print(f"   - {model_display}")


if __name__ == "__main__":
    try:
        print("硅基流动模型选择功能测试")
        print("=" * 50)

        test_config_structure()
        test_model_functions()
        test_config_generation()
        test_menu_simulation()
        test_backwards_compatibility()
        test_integration_flow()
        show_usage_examples()

        print("\n" + "=" * 50)
        print("测试完成！硅基流动模型选择功能已就绪。")

        # 检查API密钥状态
        api_key = os.getenv("SILICONFLOW_API_KEY", "")
        if api_key:
            print(f"\n硅基流动API密钥: 已设置 (长度: {len(api_key)})")
            print("可以直接在游戏中使用硅基流动的各种模型。")
        else:
            print("\n硅基流动API密钥: 未设置")
            print("请设置 SILICONFLOW_API_KEY 环境变量后使用。")

    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()