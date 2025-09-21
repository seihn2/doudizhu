"""
测试LLM配置修复
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import get_llm_config, get_available_providers, GAME_CONFIG


def test_llm_config():
    """测试LLM配置"""
    print("=== 测试LLM配置修复 ===")

    # 检查可用提供商
    available = get_available_providers()
    print(f"可用提供商: {available}")

    if available:
        # 测试自动选择提供商
        try:
            config = get_llm_config()  # 不指定提供商，应该自动选择deepseek
            print(f"自动选择的提供商配置:")
            print(f"  提供商: 已自动选择")
            print(f"  模型: {config.get('model', '未知')}")
            print(f"  API密钥: {'已配置' if config.get('api_key') else '未配置'}")
            print("[OK] 自动选择提供商成功")

        except Exception as e:
            print(f"[FAIL] 自动选择失败: {e}")

        # 测试指定deepseek提供商
        try:
            config = get_llm_config("deepseek", "fast")
            print(f"\nDeepSeek配置:")
            print(f"  模型: {config.get('model')}")
            print(f"  基础URL: {config.get('base_url')}")
            print(f"  API密钥: {'已配置' if config.get('api_key') else '未配置'}")
            print("[OK] DeepSeek配置正常")

        except Exception as e:
            print(f"[FAIL] DeepSeek配置失败: {e}")

    else:
        print("[WARNING] 没有可用的LLM提供商")

    # 检查默认配置
    print(f"\n默认LLM提供商: {GAME_CONFIG['llm_provider']}")
    print(f"默认模型类型: {GAME_CONFIG['llm_model_type']}")


if __name__ == "__main__":
    test_llm_config()