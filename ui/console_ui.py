"""
控制台用户界面模块
提供完整的控制台交互界面
"""

import sys
from typing import List, Optional, Dict, Any
from game.player import HumanPlayer
from game.game_state import GameController, GamePhase
from game.rules import RuleEngine
from ai.ai_player import AIPlayerFactory, Difficulty
from ai.card_recommender import CardRecommender
from .utils import *


class ConsoleUI:
    """控制台用户界面类"""

    def __init__(self):
        """初始化控制台界面"""
        self.controller = GameController()
        self.human_player = None
        self.ai_players = []
        self.recommender = CardRecommender()
        self.game_settings = {
            "ai_difficulty": Difficulty.MEDIUM,
            "show_ai_thinking": True,
            "auto_continue": False,
            "show_recommendations": True
        }

    def start(self):
        """启动游戏界面"""
        try:
            self.show_welcome()
            self.main_menu()
        except KeyboardInterrupt:
            self.show_goodbye()
        except Exception as e:
            print_error(f"游戏发生错误: {e}")
            self.show_goodbye()

    def show_welcome(self):
        """显示欢迎界面"""
        clear_screen()
        print_ascii_art()
        print_info("欢迎来到AI斗地主游戏！")
        print_info("在这里你可以与智能AI对手进行精彩的斗地主对战")
        wait_for_enter()

    def main_menu(self):
        """主菜单"""
        while True:
            clear_screen()
            print_title("主菜单")

            options = [
                "开始游戏",
                "游戏设置",
                "查看帮助",
                "关于游戏",
                "退出游戏"
            ]

            choice = show_menu("请选择操作", options)

            if choice == 0:
                self.start_game_flow()
            elif choice == 1:
                self.settings_menu()
            elif choice == 2:
                self.show_help_menu()
            elif choice == 3:
                self.show_about()
            elif choice == 4:
                self.show_goodbye()
                break

    def start_game_flow(self):
        """开始游戏流程"""
        clear_screen()
        print_title("开始游戏")

        # 创建玩家
        player_name = get_user_input("请输入你的姓名 (默认: 玩家): ")
        if not player_name:
            player_name = "玩家"

        self.human_player = HumanPlayer(player_name, 0)
        self.ai_players = AIPlayerFactory.create_ai_team(self.game_settings["ai_difficulty"])

        players = [self.human_player] + self.ai_players

        print_success(f"游戏开始！玩家：{player_name}")
        print_info(f"AI对手：{self.ai_players[0].name}, {self.ai_players[1].name}")
        print_info(f"AI难度：{self.game_settings['ai_difficulty'].value}")

        wait_for_enter("按回车键开始发牌...")

        # 开始游戏
        self.controller.start_game(players)
        self.run_game()

    def run_game(self):
        """运行游戏主循环"""
        # 叫地主阶段
        self.bidding_phase()

        # 游戏进行阶段
        if self.controller.state.phase == GamePhase.PLAYING:
            self.playing_phase()

        # 显示游戏结果
        if self.controller.is_game_over():
            self.show_game_result()

    def bidding_phase(self):
        """叫地主阶段"""
        clear_screen()
        print_title("叫地主阶段")

        print_info("底牌：" + format_card_display(self.controller.state.bottom_cards))
        print_separator()

        success = self.controller.bidding_phase()

        if not success:
            print_warning("没有人叫地主，重新开始游戏")
            wait_for_enter()
            return

        landlord = self.controller.state.get_landlord()
        print_success(f"{landlord.name} 成为地主！")

        if landlord == self.human_player:
            print_info("恭喜你成为地主！")
            print_hand_cards(self.human_player.get_hand_cards())

        wait_for_enter("按回车键开始游戏...")

    def playing_phase(self):
        """游戏进行阶段"""
        while not self.controller.is_game_over():
            self.show_game_state()

            current_player = self.controller.state.get_current_player()

            if current_player == self.human_player:
                self.human_turn()
            else:
                self.ai_turn()

            if not self.game_settings["auto_continue"] and current_player != self.human_player:
                wait_for_enter("按回车键继续...")

    def show_game_state(self):
        """显示游戏状态"""
        clear_screen()
        print_title(f"第 {self.controller.state.round_count + 1} 回合")

        # 显示玩家信息
        print_player_info(self.controller.state.players, self.controller.state.current_player_idx)

        # 显示上一手牌
        if self.controller.state.last_play:
            last_player = self.controller.state.players[self.controller.state.last_player_idx]
            last_play_info = {
                "player_name": last_player.name,
                "card_type": RuleEngine.get_card_type_name(self.controller.state.last_play.card_type),
                "cards": self.controller.state.last_play.cards
            }
            print_last_play(last_play_info)
        else:
            print_last_play({})

        # 如果是人类玩家回合，显示手牌
        if self.controller.state.get_current_player() == self.human_player:
            print_hand_cards(self.human_player.get_hand_cards())

    def human_turn(self):
        """人类玩家回合"""
        print(f"{Colors.BRIGHT}轮到你出牌了！{Colors.RESET}")

        while True:
            if self.controller.state.last_play:
                print_info("你可以选择跟牌或过牌")
            else:
                print_info("你是第一个出牌，可以出任意合法牌型")

            # 显示出牌推荐
            if self.game_settings["show_recommendations"]:
                self.show_recommendations()

            choice = get_user_input("请输入要出的牌（用空格分隔，输入'pass'跳过，输入'help'查看帮助，输入'rec'查看推荐）: ")

            if choice.lower() in ['help', '帮助', 'h']:
                self.show_card_input_help()
                continue
            elif choice.lower() in ['rec', 'recommend', '推荐', 'r']:
                self.show_detailed_recommendations()
                continue

            if choice.lower() in ['pass', 'p', '过', '跳过']:
                if self.controller.state.last_play is None:
                    print_error("第一次出牌不能跳过！")
                    continue
                break

            # 解析用户输入
            try:
                cards_to_play = self.parse_card_input(choice)
                if not cards_to_play:
                    print_error("请输入有效的牌")
                    continue

                if not self.human_player.hand.has_cards(cards_to_play):
                    print_error("你没有这些牌")
                    continue

                # 首先验证牌型是否有效
                pattern = RuleEngine.analyze_cards(cards_to_play)
                if pattern.card_type.value == "invalid":
                    print_error("无效的牌型，请重新选择")
                    continue

                # 检查是否可以出这手牌
                if not RuleEngine.can_follow(cards_to_play, self.controller.state.last_play):
                    print_error("这手牌无法跟上一手牌")
                    continue

                # 执行出牌
                self.human_player.play_cards(cards_to_play)
                self.controller.state.last_play = pattern
                self.controller.state.last_player_idx = self.controller.state.current_player_idx
                self.controller.state.reset_pass_count()

                type_name = RuleEngine.get_card_type_name(pattern.card_type)
                print_success(f"你出了 {type_name}: {format_card_display(cards_to_play)}")

                # 记录动作
                self.controller.state.log_action("play_cards", 0, cards_to_play,
                                                card_type=pattern.card_type.value)

                # 检查游戏是否结束
                if self.human_player.is_hand_empty():
                    self.controller.state.winner_idx = 0
                    self.controller.state.phase = GamePhase.ENDED
                    self.controller.state.log_action("game_end", 0)
                    return

                break

            except Exception as e:
                print_error(f"输入错误: {e}")

        # 切换到下一个玩家
        self.controller.state.next_player()
        self.controller.state.round_count += 1

    def ai_turn(self):
        """AI玩家回合"""
        if not self.controller.play_turn():
            print_error("AI出牌失败")

    def parse_card_input(self, input_str: str) -> List:
        """解析用户卡牌输入"""
        if not input_str.strip():
            return []

        parts = input_str.strip().split()
        cards_to_play = []

        value_map = {
            '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
            'j': 11, 'q': 12, 'k': 13, 'a': 14, '2': 15,
            '小王': 16, '大王': 17, 'joker': 16, 'JOKER': 17
        }

        # 统计需要的牌值
        needed_values = []
        for part in parts:
            part_lower = part.lower()
            if part_lower in value_map:
                needed_values.append(value_map[part_lower])

        # 从手牌中找出对应的牌
        available_cards = self.human_player.get_hand_cards()
        for value in needed_values:
            for card in available_cards:
                if card.value == value and card not in cards_to_play:
                    cards_to_play.append(card)
                    break

        return cards_to_play

    def show_card_input_help(self):
        """显示卡牌输入帮助"""
        print_separator()
        print(f"{Colors.BRIGHT}卡牌输入帮助:{Colors.RESET}")
        print("• 数字3-10：直接输入数字")
        print("• J、Q、K、A、2：输入对应字母")
        print("• 小王：输入'小王'或'joker'")
        print("• 大王：输入'大王'或'JOKER'")
        print("• 示例：'3 4 5'（顺子）、'7 7'（对子）、'k k k'（三张K）")
        print("• 输入'pass'跳过出牌")
        print_separator()

    def show_game_result(self):
        """显示游戏结果"""
        result = self.controller.get_game_result()
        print_game_result(result)

        # 询问是否再来一局
        while True:
            choice = get_user_input("是否再来一局？(y/n): ", ["y", "yes", "n", "no", "是", "否"])
            if choice.lower() in ['y', 'yes', '是']:
                self.start_game_flow()
                break
            elif choice.lower() in ['n', 'no', '否']:
                break

    def settings_menu(self):
        """设置菜单"""
        while True:
            clear_screen()
            print_title("游戏设置")

            current_settings = [
                f"AI难度: {self.game_settings['ai_difficulty'].value}",
                f"显示AI思考: {'是' if self.game_settings['show_ai_thinking'] else '否'}",
                f"自动继续: {'是' if self.game_settings['auto_continue'] else '否'}",
                f"出牌推荐: {'是' if self.game_settings['show_recommendations'] else '否'}"
            ]

            for i, setting in enumerate(current_settings, 1):
                print(f"{i}. {setting}")

            print(f"{len(current_settings) + 1}. 返回主菜单")
            print()

            try:
                choice = int(get_user_input(f"请选择要修改的设置 (1-{len(current_settings) + 1}): "))

                if choice == 1:
                    self.change_ai_difficulty()
                elif choice == 2:
                    self.game_settings["show_ai_thinking"] = not self.game_settings["show_ai_thinking"]
                elif choice == 3:
                    self.game_settings["auto_continue"] = not self.game_settings["auto_continue"]
                elif choice == 4:
                    self.game_settings["show_recommendations"] = not self.game_settings["show_recommendations"]
                elif choice == len(current_settings) + 1:
                    break
                else:
                    print_error("无效选择")
                    wait_for_enter()

            except ValueError:
                print_error("请输入有效数字")
                wait_for_enter()

    def change_ai_difficulty(self):
        """更改AI难度"""
        difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
        names = ["简单", "中等", "困难"]

        choice = show_menu("选择AI难度", names)
        self.game_settings["ai_difficulty"] = difficulties[choice]
        print_success(f"AI难度已设置为: {names[choice]}")
        wait_for_enter()

    def show_help_menu(self):
        """显示帮助菜单"""
        clear_screen()
        show_help()
        wait_for_enter()

    def show_about(self):
        """显示关于信息"""
        clear_screen()
        print_title("关于游戏")

        about_text = f"""
{Colors.BRIGHT}AI斗地主 v1.0{Colors.RESET}

这是一个基于Python开发的本地单人斗地主游戏。

{Colors.YELLOW}特色功能:{Colors.RESET}
• 智能AI对手，多种难度可选
• 完整的斗地主规则实现
• 友好的控制台交互界面
• 支持所有标准牌型

{Colors.YELLOW}技术实现:{Colors.RESET}
• Python 3.7+
• 面向对象设计
• 模块化架构
• 智能AI策略

{Colors.YELLOW}开发信息:{Colors.RESET}
• 版本: 1.0.0
• 开发语言: Python
• 支持平台: Windows, Linux, macOS

感谢你使用AI斗地主游戏，祝你游戏愉快！
        """

        print(about_text)
        wait_for_enter()

    def show_recommendations(self):
        """显示简要推荐"""
        if not self.human_player:
            return

        try:
            recommendations = self.recommender.get_recommendations(
                self.human_player.get_hand_cards(),
                self.controller.state.last_play,
                self.controller.state.get_game_info(),
                max_suggestions=3
            )

            if recommendations:
                print_separator("=", 30)
                print(f"{Colors.YELLOW}[建议] 出牌建议:{Colors.RESET}")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"  {i}. {self.recommender.format_recommendation(rec)}")
                print_separator("=", 30)
        except Exception as e:
            # 推荐系统出错不影响游戏进行
            pass

    def show_detailed_recommendations(self):
        """显示详细推荐"""
        if not self.human_player:
            return

        clear_screen()
        print_title("详细出牌推荐")

        try:
            recommendations = self.recommender.get_recommendations(
                self.human_player.get_hand_cards(),
                self.controller.state.last_play,
                self.controller.state.get_game_info(),
                max_suggestions=8
            )

            if recommendations:
                print_hand_cards(self.human_player.get_hand_cards())

                if self.controller.state.last_play:
                    last_player = self.controller.state.players[self.controller.state.last_player_idx]
                    last_play_info = {
                        "player_name": last_player.name,
                        "card_type": RuleEngine.get_card_type_name(self.controller.state.last_play.card_type),
                        "cards": self.controller.state.last_play.cards
                    }
                    print_last_play(last_play_info)

                print(f"\n{Colors.BRIGHT}[推荐] 推荐方案:{Colors.RESET}")
                for i, rec in enumerate(recommendations, 1):
                    priority_color = Colors.GREEN if rec['priority'] >= 7 else Colors.YELLOW if rec['priority'] >= 5 else Colors.WHITE
                    print(f"  {priority_color}{i}. {self.recommender.format_recommendation(rec)}{Colors.RESET}")

                print(f"\n{Colors.CYAN}说明: 优先级越高的建议越推荐使用{Colors.RESET}")
            else:
                print_warning("没有找到合适的推荐")

        except Exception as e:
            print_error(f"推荐系统出错: {e}")

        wait_for_enter("\n按回车键返回游戏...")

    def show_goodbye(self):
        """显示再见信息"""
        clear_screen()
        print_title("再见")
        print_info("感谢游戏，期待下次相见！")
        print(f"\n{Colors.CYAN}♠ ♥ ♦ ♣ 游戏结束 ♣ ♦ ♥ ♠{Colors.RESET}\n")
        sys.exit(0)


if __name__ == "__main__":
    ui = ConsoleUI()
    ui.start()