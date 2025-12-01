import os 
from dotenv import load_dotenv

# Load environment variables (API keys, etc.)
_ = load_dotenv()

# Get NPX path from environment (required for all configurations)
NPX_EXECUTABLE_PATH = os.environ.get("NPX_EXECUTABLE_PATH")

# Validate that the NPX executable path is available
if not NPX_EXECUTABLE_PATH:
    print("Error: NPX_EXECUTABLE_PATH not found in environment variables.")
    print("Please make sure you have a .env file with NPX_EXECUTABLE_PATH=/path/to/npx")
    exit(1)


def create_notion_servers_config(notion_token: str):
    """
    Create SERVERS configuration with the provided Notion token.
    
    Args:
        notion_token: User's Notion integration token
        
    Returns:
        dict: SERVERS configuration for MCP client
    """
    if not notion_token:
        raise ValueError("Notion token is required")
    
    return {
        "notion": {
            "transport": "stdio",
            "command": NPX_EXECUTABLE_PATH,
            "args": ["-y", "@notionhq/notion-mcp-server"],
            "env": {
                "NOTION_TOKEN": notion_token
            }
        }
    }


# Default SERVERS config (uses env var if available, otherwise None)
# This is kept for backward compatibility but will be replaced by user input
DEFAULT_NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
SERVERS = create_notion_servers_config(DEFAULT_NOTION_TOKEN) if DEFAULT_NOTION_TOKEN else None

