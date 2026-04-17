import os
import argparse
from dotenv import load_dotenv
from rag.chat import ChanvipChat
from web.main import run_web_app

# Load environment variables
load_dotenv()

def main():
    # Parse command line arguments to select running mode
    parser = argparse.ArgumentParser(description="chanvip.skills Startup Program (Chan Master Full-Domain AI Skill)")
    parser.add_argument("--mode", type=str, default="cli", choices=["cli", "web"], 
                        help="Running mode: cli (command line), web (Web interface), default cli")
    args = parser.parse_args()

    # Initialize Chan Master dialogue instance
    chat = ChanvipChat()

    # Start the corresponding mode
    if args.mode == "cli":
        print("="*50)
        print("chanvip.skills (Chan Master Full-Domain AI Skill)")
        print("="*50)
        print("Tip: Enter a question to chat with the Chan Master style AI, enter 'exit' to quit")
        print("Query example: Chan Master, what is Chan Theory's central hub? / Stock + divergence judgment")
        print("="*50)
        
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() == "exit":
                print("Chan Master Style AI: Thank you for the exchange, wish you gain something, goodbye!")
                break
            if not user_input.strip():
                print("Chan Master Style AI: Please enter a specific question, and I will interpret it for you.")
                continue
            # Generate response
            response = chat.get_response(user_input)
            print(f"\nChan Master Style AI: {response}")
    
    elif args.mode == "web":
        # Start Web interface
        host = os.getenv("WEB_HOST", "0.0.0.0")
        port = int(os.getenv("WEB_PORT", 8000))
        print(f"Web interface started successfully, access address: http://{host}:{port}")
        run_web_app(chat)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Program running error: {str(e)}")
        print("Please check the environment configuration (.env file) or whether the dependencies are fully installed, refer to the README.md deployment tutorial")
