"""
chanvip.skills — 主程序入口
Chan Master Full-Domain AI Skill Package
"""
import os
import argparse
from dotenv import load_dotenv
from rag.chat import ChanvipChat
from web.main import run_web_app

load_dotenv()

def main():
    parser = argparse.ArgumentParser(
        description="chanvip.skills — 缠中说禅 · 全域AI技能包",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py --mode cli          # 命令行交互模式
  python main.py --mode web          # 网页界面模式
  python main.py --mode cli --query "禅师，什么是走势必完美？"
        """
    )
    parser.add_argument("--mode", type=str, default="cli",
                        choices=["cli", "web"],
                        help="运行模式: cli=命令行, web=网页界面")
    parser.add_argument("--query", type=str, default=None,
                        help="直接传入问题（仅cli模式，自动化使用）")
    args = parser.parse_args()

    chat = ChanvipChat()

    if args.mode == "cli":
        if args.query:
            print(f"\n你: {args.query}")
            response = chat.get_response(args.query)
            print(f"\n禅师: {response}\n")
            return

        print("=" * 52)
        print("  chanvip.skills  —  缠中说禅 · 全域AI技能包")
        print("=" * 52)
        print("  覆盖: 股票 · 音乐 · 经济 · 诗歌 · 哲学")
        print("  输入问题即可对话，输入 exit 退出")
        print("=" * 52)

        while True:
            try:
                user_input = input("\n你: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\n禅师: 有缘再见，修行路上再见！")
                break

            if user_input.lower() in ("exit", "quit", "q"):
                print("禅师: 有缘再见，修行路上再见！")
                break
            if not user_input:
                print("禅师: 请提出具体问题，心诚则灵。")
                continue

            response = chat.get_response(user_input)
            print(f"\n禅师: {response}")

    elif args.mode == "web":
        host = os.getenv("WEB_HOST", "0.0.0.0")
        port = int(os.getenv("WEB_PORT", "8000"))
        print(f"\n🚀 chanvip.skills Web 服务启动中...")
        print(f"   访问地址: http://{host}:{port}")
        print(f"   按 Ctrl+C 停止服务\n")
        run_web_app(chat)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n禅师: 服务已停止，有缘再见！")
    except Exception as e:
        print(f"\n⚠️ 运行时错误: {e}")
        print("请检查: 1) .env 文件是否配置正确  2) 依赖是否完整安装")
        print("运行 'python setup_knowledge.py' 初始化知识库")
