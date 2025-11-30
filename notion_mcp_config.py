import os 
from dotenv import load_dotenv

# Load environment variables (API keys, etc.)
_ = load_dotenv()

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
NPX_EXECUTABLE_PATH = os.environ.get("NPX_EXECUTABLE_PATH")

# Validate that the Notion token is available
if not NOTION_TOKEN:
    print("Error: NOTION_TOKEN not found in environment variables.")
    print("Please make sure you have a .env file with NOTION_TOKEN=your_token")
    exit(1)

# Validate that the NPX executable path is available
if not NPX_EXECUTABLE_PATH:
    print("Error: NPX_EXECUTABLE_PATH not found in environment variables.")
    print("Please make sure you have a .env file with NPX_EXECUTABLE_PATH=/path/to/npx")
    exit(1)


SERVERS = {
    "notion": {
        "transport": "stdio",  # Use stdio for communication
        "command": NPX_EXECUTABLE_PATH,  # NPX executable path from environment
        "args": ["-y", "@notionhq/notion-mcp-server"],  # Official open-source Notion MCP server
        "env": {
            "NOTION_TOKEN": NOTION_TOKEN  # Pass the token as environment variable
        }
    }
}

