"""
支持LLM AI的斗地主游戏主程序
可以选择使用算法AI或大语言模型AI
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.console_ui import ConsoleUI
from ai.ai_player import AIPlayerFactory, Difficulty
from ai.llm_player import create_llm_player
from config import get_llm_config, get_available_providers, GAME_CONFIG
from game.player import HumanPlayer


class EnhancedConsoleUI(ConsoleUI):
    """增强的控制台界面，支持LLM AI"""

    def __init__(self):
        super().__init__()
        self.llm_enabled = False

    def main_menu(self):
        """增强的主菜单"""
        while True:
            from ui.utils import clear_screen, print_title, show_menu

            clear_screen()
            print_title("AI斗地主 - 增强版")

            options = [
                "开始游戏 (算法AI)",
                "开始游戏 (LLM AI)" if get_available_providers() else "开始游戏 (LLM AI) - 需要配置API",
                "AI类型设置",
                "游戏设置",
                "查看帮助",
                "关于游戏",
                "退出游戏"
            ]

            choice = show_menu("请选择操作", options)

            if choice == 0:
                self.llm_enabled = False
                self.start_game_flow()
            elif choice == 1:
                if get_available_providers():
                    self.llm_enabled = True
                    self.start_game_flow()
                else:
                    self.show_llm_setup_help()
            elif choice == 2:
                self.ai_type_menu()
            elif choice == 3:
                self.settings_menu()
            elif choice == 4:
                self.show_help_menu()
            elif choice == 5:
                self.show_about()
            elif choice == 6:
                self.show_goodbye()
                break

    def ai_type_menu(self):
        """AI类型设置菜单"""
        from ui.utils import clear_screen, print_title, show_menu, print_info, wait_for_enter

        while True:
            clear_screen()
            print_title("AI类型设置")

            print_info(f"当前AI类型: {'LLM AI' if self.llm_enabled else '算法AI'}")

            if get_available_providers():
                providers = get_available_providers()
                print_info(f"可用LLM提供商: {', '.join(providers)}")
            else:
                print_info("未配置LLM API密钥")

            options = [
                "使用算法AI（本地，快速）",
                "使用LLM AI（在线，智能）" if get_available_providers() else "配置LLM API",
                "返回主菜单"
            ]

            choice = show_menu("选择AI类型", options)

            if choice == 0:
                self.llm_enabled = False
                print_info("已切换到算法AI")
                wait_for_enter()
                break
            elif choice == 1:
                if get_available_providers():
                    self.llm_enabled = True
                    self.select_llm_provider()
                    break
                else:
                    self.show_llm_setup_help()
            elif choice == 2:
                break

    def select_llm_provider(self):
        """选择LLM提供商"""
        from ui.utils import show_menu, print_success, wait_for_enter

        providers = get_available_providers()
        if not providers:
            return

        choice = show_menu("选择LLM提供商", providers + ["返回"])

        if choice < len(providers):
            selected_provider = providers[choice]
            GAME_CONFIG["llm_provider"] = selected_provider
            print_success(f"已选择 {selected_provider.upper()} 作为LLM提供商")
            wait_for_enter()

    def start_game_flow(self):
        """开始游戏流程（增强版）"""
        from ui.utils import clear_screen, print_title, get_user_input, print_success, print_info, wait_for_enter

        clear_screen()
        print_title("开始游戏")

        # 创建人类玩家
        player_name = get_user_input("请输入你的姓名 (默认: 玩家): ")
        if not player_name:
            player_name = "玩家"

        self.human_player = HumanPlayer(player_name, 0)

        # 创建AI玩家
        if self.llm_enabled:
            print_info("正在创建LLM AI对手...")
            self.ai_players = self.create_llm_ai_team()
        else:
            print_info("正在创建算法AI对手...")
            self.ai_players = AIPlayerFactory.create_ai_team(self.game_settings["ai_difficulty"])

        players = [self.human_player] + self.ai_players

        print_success(f"游戏开始！玩家：{player_name}")

        for ai in self.ai_players:
            ai_type = "LLM AI" if self.llm_enabled else f"算法AI ({ai.difficulty.value})"
            print_info(f"AI对手：{ai.name} ({ai_type})")

        wait_for_enter("按回车键开始发牌...")

        # 开始游戏
        self.controller.start_game(players)
        self.run_game()

    def create_llm_ai_team(self):
        """创建LLM AI队伍"""
        # 自动使用可用的提供商
        available_providers = get_available_providers()
        if not available_providers:
            from ui.utils import print_error
            print_error("没有可用的LLM提供商，降级使用算法AI")
            return AIPlayerFactory.create_ai_team(Difficulty.MEDIUM)

        provider = available_providers[0]  # 使用第一个可用的提供商
        model_type = GAME_CONFIG.get("llm_model_type", "fast")

        try:
            config = get_llm_config(provider, model_type)
            ai_names = ["AI助手", "智能对手"]

            from ui.utils import print_info
            print_info(f"使用 {provider.upper()} 提供的LLM AI")

            llm_players = []
            for i, name in enumerate(ai_names):
                player = create_llm_player(
                    name=name,
                    player_id=i + 1,
                    provider=provider,
                    api_key=config["api_key"],
                    model=config["model"]
                )
                llm_players.append(player)

            return llm_players

        except Exception as e:
            from ui.utils import print_error
            print_error(f"创建LLM AI失败: {e}")
            print_error("降级使用算法AI")
            return AIPlayerFactory.create_ai_team(Difficulty.MEDIUM)

    def show_llm_setup_help(self):
        """显示LLM设置帮助"""
        from ui.utils import clear_screen, print_title, print_info, wait_for_enter

        clear_screen()
        print_title("LLM AI 设置帮助")

        help_text = """
要使用大语言模型AI，需要先配置API密钥：

1. 选择一个LLM提供商：
   • OpenAI (ChatGPT)
   • Anthropic (Claude)
   • DeepSeek
   • Moonshot

2. 获取API密钥：
   • 访问提供商官网注册账号
   • 在API设置中生成密钥

3. 设置环境变量：
   Windows:
   set OPENAI_API_KEY=sk-your-key-here

   Linux/Mac:
   export OPENAI_API_KEY=sk-your-key-here

4. 重启游戏即可使用LLM AI

注意：
• LLM AI需要网络连接
• 会产生API调用费用
• 响应速度较慢（1-5秒）
• 但策略更加智能和有趣
        """

        print_info(help_text)
        wait_for_enter()

    def show_about(self):
        """显示关于信息（增强版）"""
        from ui.utils import clear_screen, print_title, wait_for_enter, Colors

        clear_screen()
        print_title("关于游戏")

        about_text = f"""
{Colors.BRIGHT}AI斗地主 - 增强版 v1.1{Colors.RESET}

这是一个支持多种AI类型的本地斗地主游戏。

{Colors.YELLOW}AI类型:{Colors.RESET}
• 算法AI: 基于规则和启发式算法，快速本地运行
• LLM AI: 基于大语言模型，智能分析和决策

{Colors.YELLOW}支持的LLM:{Colors.RESET}
• OpenAI GPT-4o / GPT-4o-mini
• Anthropic Claude-3
• DeepSeek Chat
• Moonshot AI

{Colors.YELLOW}特色功能:{Colors.RESET}
• 多种AI难度可选
• 完整的斗地主规则实现
• 友好的控制台交互界面
• 支持所有标准牌型
• 智能API故障降级

{Colors.YELLOW}技术实现:{Colors.RESET}
• Python 3.7+
• 异步API调用
• 模块化架构
• 智能提示词工程

感谢你使用AI斗地主游戏，祝你游戏愉快！
        """

        print(about_text)
        wait_for_enter()


def main():
    """主程序入口"""
    try:
        # 检查依赖
        try:
            import colorama
            import tabulate
            import aiohttp
        except ImportError as e:
            print("缺少依赖包，请运行:")
            print("pip install colorama tabulate aiohttp")
            print(f"错误详情: {e}")
            return

        # 启动增强版游戏界面
        ui = EnhancedConsoleUI()
        ui.start()

    except KeyboardInterrupt:
        print("\n\n游戏被用户中断")
    except Exception as e:
        print(f"\n游戏发生致命错误: {e}")
        print("请检查错误信息或联系开发者")


if __name__ == "__main__":
    main()