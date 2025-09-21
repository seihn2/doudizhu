"""
项目配置文件
包含API密钥、模型配置等
"""

import os
from typing import Dict, Any

# LLM API配置
LLM_CONFIGS = {
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "base_url": "https://api.openai.com/v1",
        "models": {
            "fast": "gpt-4o-mini",
            "smart": "gpt-4o",
            "cheap": "gpt-3.5-turbo"
        }
    },
    "anthropic": {
        "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
        "base_url": "https://api.anthropic.com",
        "models": {
            "fast": "claude-3-haiku-20240307",
            "smart": "claude-3-sonnet-20240229",
            "cheap": "claude-3-haiku-20240307"
        }
    },
    "deepseek": {
        "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
        "base_url": "https://api.deepseek.com",
        "models": {
            "fast": "deepseek-chat",
            "smart": "deepseek-coder",
            "cheap": "deepseek-chat"
        }
    },
    "moonshot": {
        "api_key": os.getenv("MOONSHOT_API_KEY", ""),
        "base_url": "https://api.moonshot.cn/v1",
        "models": {
            "fast": "moonshot-v1-8k",
            "smart": "moonshot-v1-32k",
            "cheap": "moonshot-v1-8k"
        }
    },
    "siliconflow": {
        "api_key": os.getenv("SILICONFLOW_API_KEY", ""),
        "base_url": "https://api.siliconflow.cn/v1",
        "models": {
            "fast": "Qwen/Qwen2.5-7B-Instruct",
            "smart": "deepseek-ai/DeepSeek-V2.5",
            "cheap": "Qwen/Qwen2.5-7B-Instruct",
            # 具体模型选择
            "qwen2.5-7b": "Qwen/Qwen2.5-7B-Instruct",
            "qwen2.5-14b": "Qwen/Qwen2.5-14B-Instruct",
            "qwen2.5-32b": "Qwen/Qwen2.5-32B-Instruct",
            "qwen2.5-72b": "Qwen/Qwen2.5-72B-Instruct",
            "deepseek-v2.5": "deepseek-ai/DeepSeek-V2.5",
            "deepseek-coder-v2": "deepseek-ai/DeepSeek-Coder-V2-Instruct",
            "claude-3.5-sonnet": "anthropic/claude-3-5-sonnet-20241022",
            "claude-3.5-haiku": "anthropic/claude-3-5-haiku-20241022",
            "gpt-4o": "OpenAI/gpt-4o",
            "gpt-4o-mini": "OpenAI/gpt-4o-mini",
            "yi-lightning": "01-ai/Yi-Lightning",
            "yi-large": "01-ai/Yi-Large",
            "chatglm3-6b": "THUDM/chatglm3-6b",
            "llama3.1-8b": "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "llama3.1-70b": "meta-llama/Meta-Llama-3.1-70B-Instruct",
            "llama3.1-405b": "meta-llama/Meta-Llama-3.1-405B-Instruct",
            "internlm2.5-7b": "internlm/internlm2_5-7b-chat",
            "internlm2.5-20b": "internlm/internlm2_5-20b-chat"
        },
        # 模型分类，用于界面显示
        "model_categories": {
            "推荐模型": {
                "qwen2.5-7b": "Qwen2.5-7B (快速、经济)",
                "deepseek-v2.5": "DeepSeek-V2.5 (智能推理)",
                "claude-3.5-sonnet": "Claude-3.5-Sonnet (高质量)",
                "gpt-4o-mini": "GPT-4o-mini (均衡)"
            },
            "Qwen系列": {
                "qwen2.5-7b": "Qwen2.5-7B",
                "qwen2.5-14b": "Qwen2.5-14B",
                "qwen2.5-32b": "Qwen2.5-32B",
                "qwen2.5-72b": "Qwen2.5-72B"
            },
            "DeepSeek系列": {
                "deepseek-v2.5": "DeepSeek-V2.5",
                "deepseek-coder-v2": "DeepSeek-Coder-V2"
            },
            "Claude系列": {
                "claude-3.5-sonnet": "Claude-3.5-Sonnet",
                "claude-3.5-haiku": "Claude-3.5-Haiku"
            },
            "GPT系列": {
                "gpt-4o": "GPT-4o",
                "gpt-4o-mini": "GPT-4o-mini"
            },
            "其他模型": {
                "yi-lightning": "Yi-Lightning",
                "yi-large": "Yi-Large",
                "chatglm3-6b": "ChatGLM3-6B",
                "llama3.1-8b": "Llama3.1-8B",
                "llama3.1-70b": "Llama3.1-70B",
                "llama3.1-405b": "Llama3.1-405B",
                "internlm2.5-7b": "InternLM2.5-7B",
                "internlm2.5-20b": "InternLM2.5-20B"
            }
        }
    }
}

# 游戏配置
GAME_CONFIG = {
    "default_ai_difficulty": "medium",  # easy, medium, hard
    "enable_llm_ai": False,  # 是否启用LLM AI
    "llm_provider": "deepseek",  # 默认LLM提供商
    "llm_model_type": "fast",  # fast, smart, cheap (用于非硅基流动提供商)
    "llm_model_key": None,  # 具体模型key (用于硅基流动等支持多模型的提供商)
    "max_thinking_time": 10.0,  # AI最大思考时间（秒）
    "auto_continue": False,  # 是否自动继续游戏
    "show_ai_reasoning": True,  # 是否显示AI推理过程
}

# UI配置
UI_CONFIG = {
    "enable_colors": True,  # 是否启用彩色输出
    "show_debug_info": False,  # 是否显示调试信息
    "card_display_style": "unicode",  # unicode, ascii
}

def get_llm_config(provider: str = None, model_type: str = "fast") -> Dict[str, Any]:
    """获取LLM配置"""
    # 如果没有指定提供商，自动选择可用的
    if provider is None:
        available_providers = get_available_providers()
        if available_providers:
            provider = available_providers[0]
        else:
            raise ValueError("没有可用的LLM提供商，请配置API密钥")

    if provider not in LLM_CONFIGS:
        raise ValueError(f"不支持的LLM提供商: {provider}")

    config = LLM_CONFIGS[provider].copy()

    if model_type in config["models"]:
        config["model"] = config["models"][model_type]
    else:
        config["model"] = config["models"]["fast"]

    return config

def validate_llm_config(provider: str) -> bool:
    """验证LLM配置是否有效"""
    config = LLM_CONFIGS.get(provider, {})
    api_key = config.get("api_key", "")

    if not api_key:
        print(f"警告：未设置{provider.upper()}的API密钥")
        return False

    # 检查API密钥长度，不同提供商格式不同
    if len(api_key) < 10:
        print(f"警告：{provider.upper()}的API密钥长度可能不正确")
        return False

    return True

def get_available_providers() -> list:
    """获取可用的LLM提供商列表"""
    available = []
    for provider in LLM_CONFIGS.keys():
        if validate_llm_config(provider):
            available.append(provider)
    return available

def get_siliconflow_models() -> Dict[str, Any]:
    """获取硅基流动的模型分类和选择"""
    if "siliconflow" not in LLM_CONFIGS:
        return {}

    config = LLM_CONFIGS["siliconflow"]
    return config.get("model_categories", {})

def get_model_display_name(provider: str, model_key: str) -> str:
    """获取模型的显示名称"""
    if provider == "siliconflow" and "siliconflow" in LLM_CONFIGS:
        categories = LLM_CONFIGS["siliconflow"].get("model_categories", {})
        for category_name, models in categories.items():
            if model_key in models:
                return models[model_key]

    # 默认返回模型key
    return model_key

def get_llm_config_with_model(provider: str, model_key: str) -> Dict[str, Any]:
    """获取指定模型的LLM配置"""
    if provider not in LLM_CONFIGS:
        raise ValueError(f"不支持的LLM提供商: {provider}")

    config = LLM_CONFIGS[provider].copy()

    if model_key in config["models"]:
        config["model"] = config["models"][model_key]
    else:
        # 如果模型不存在，使用默认的fast模型
        config["model"] = config["models"].get("fast", list(config["models"].values())[0])

    return config

# 环境变量示例（需要在系统中设置）
EXAMPLE_ENV_VARS = """
# 在系统环境变量或.env文件中设置以下变量：

# OpenAI
export OPENAI_API_KEY="sk-your-openai-key-here"

# Anthropic (Claude)
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"

# DeepSeek
export DEEPSEEK_API_KEY="sk-your-deepseek-key-here"

# Moonshot
export MOONSHOT_API_KEY="sk-your-moonshot-key-here"
"""

if __name__ == "__main__":
    print("=== LLM配置检查 ===")

    for provider in LLM_CONFIGS.keys():
        config = get_llm_config(provider)
        has_key = bool(config.get("api_key"))
        status = "[OK]" if has_key else "[NO]"
        print(f"{provider.upper()}: {status} API密钥")

    print(f"\n可用提供商: {get_available_providers()}")

    if not get_available_providers():
        print("\n" + "="*50)
        print("需要设置API密钥才能使用LLM AI功能")
        print(EXAMPLE_ENV_VARS)