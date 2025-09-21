"""
游戏启动脚本
自动检测配置并启动合适的版本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import get_available_providers


def main():
    """主启动函数"""
    print("=== AI斗地主游戏启动器 ===")
    print()

    # 检查LLM配置
    available_providers = get_available_providers()

    if available_providers:
        print(f"[信息] 检测到可用的LLM提供商: {', '.join(available_providers)}")
        print("[信息] 启动增强版游戏（支持LLM AI + 出牌推荐）")
        print()

        # 启动增强版
        try:
            from main_with_llm import EnhancedConsoleUI
            ui = EnhancedConsoleUI()
            ui.start()
        except Exception as e:
            print(f"[错误] 增强版启动失败: {e}")
            print("[信息] 降级到基础版")
            fallback_to_basic()

    else:
        print("[信息] 未检测到LLM API配置")
        print("[信息] 启动基础版游戏（算法AI + 出牌推荐）")
        print()
        fallback_to_basic()


def fallback_to_basic():
    """降级到基础版"""
    try:
        from ui.console_ui import ConsoleUI
        ui = ConsoleUI()
        ui.start()
    except Exception as e:
        print(f"[错误] 基础版启动失败: {e}")
        print("请检查依赖是否正确安装: pip install -r requirements.txt")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n游戏被用户中断")
    except Exception as e:
        print(f"\n启动失败: {e}")
        print("请检查项目完整性和依赖安装")