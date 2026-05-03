"""Main entry point for the PDF Conversational Agent"""

import os
import sys
from dotenv import load_dotenv
from app.ui import ChatbotUI


def main():
    """Main function to run the chatbot"""
    
    # Load environment variables
    load_dotenv()
    
    # Verify required environment variables
    if not os.getenv("HF_API_TOKEN"):
        print("Error: HF_API_TOKEN not found in environment variables")
        print("Please set HF_API_TOKEN in your .env file")
        sys.exit(1)
    
    # Initialize and launch UI
    print("Starting PDF Conversational Agent...")
    chatbot_ui = ChatbotUI()
    
    try:
        chatbot_ui.launch(share=False, debug=True)
    except Exception as e:
        print(f"Error launching chatbot: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
