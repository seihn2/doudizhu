"""
调试LLM配置问题
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import LLM_CONFIGS, validate_llm_config, get_available_providers, get_llm_config


def debug_llm_config():
    """调试LLM配置"""
    print("=== LLM配置调试 ===")

    # 1. 检查环境变量
    print("\n1. 环境变量检查:")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
    print(f"   DEEPSEEK_API_KEY: {'已设置' if deepseek_key else '未设置'}")
    if deepseek_key:
        print(f"   密钥长度: {len(deepseek_key)}")
        print(f"   密钥前缀: {deepseek_key[:10]}...")

    # 2. 检查配置字典
    print("\n2. 配置字典检查:")
    deepseek_config = LLM_CONFIGS.get("deepseek", {})
    print(f"   DeepSeek配置存在: {'是' if deepseek_config else '否'}")
    if deepseek_config:
        api_key = deepseek_config.get("api_key", "")
        print(f"   API密钥: {'已配置' if api_key else '未配置'}")
        print(f"   基础URL: {deepseek_config.get('base_url', '未设置')}")
        print(f"   模型列表: {deepseek_config.get('models', {})}")

    # 3. 验证函数测试
    print("\n3. 验证函数测试:")
    is_valid = validate_llm_config("deepseek")
    print(f"   DeepSeek验证结果: {'通过' if is_valid else '失败'}")

    # 4. 可用提供商列表
    print("\n4. 可用提供商:")
    available = get_available_providers()
    print(f"   可用列表: {available}")

    # 5. 配置获取测试
    print("\n5. 配置获取测试:")
    try:
        config = get_llm_config("deepseek")
        print(f"   获取配置: 成功")
        print(f"   模型: {config.get('model')}")
        print(f"   API密钥存在: {'是' if config.get('api_key') else '否'}")
    except Exception as e:
        print(f"   获取配置: 失败 - {e}")

    # 6. 自动选择测试
    print("\n6. 自动选择测试:")
    try:
        config = get_llm_config()  # 不指定提供商
        print(f"   自动选择: 成功")
    except Exception as e:
        print(f"   自动选择: 失败 - {e}")


if __name__ == "__main__":
    debug_llm_config()