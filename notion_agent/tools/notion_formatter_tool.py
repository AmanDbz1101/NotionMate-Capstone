"""
Notion Formatter Tool

Formats content into Notion blocks using the NotionFormatterAgent.
"""

from google.adk.tools.tool_context import ToolContext
from notion_agent.agents.notion_formatter_agent import NotionFormatterAgent


def format_notion_blocks_tool(tool_context: ToolContext) -> str:
    """Format content into Notion blocks"""
    topic = tool_context.state.get("topic", "Untitled Note")
    summary = tool_context.state.get("summary", "")
    image_url = tool_context.state.get("image_url", "")
    
    if not summary:
        error_msg = "No summary available for formatting"
        return error_msg
    
    try:
        # Initialize formatter agent
        formatter = NotionFormatterAgent()
        
        # Format content
        formatting = formatter.format_content(topic, summary, image_url)
        blocks = formatter.blocks_to_notion_format(formatting)
        
        # Store in session state
        tool_context.state["notion_blocks"] = blocks
        
        return f"Created {len(blocks)} Notion blocks successfully"
        
    except Exception as e:
        error_msg = f"Error formatting Notion blocks: {str(e)}"
        return error_msg
