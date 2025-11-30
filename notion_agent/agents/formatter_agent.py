"""
Notion Formatter Agent (ADK Agent)

Formats the summary and image into Notion-compatible blocks.
"""

from google.adk.agents import LlmAgent
from ..tools.notion_formatter_tool import format_notion_blocks_tool


GEMINI_MODEL = "gemini-2.0-flash"


formatter_agent = LlmAgent(
    name="NotionFormatterAgent",
    model=GEMINI_MODEL,
    description="Formats the summary and image into Notion-compatible blocks",
    instruction="""You are a Notion Formatter Agent.
You have access to the 'format_notion_blocks_tool' function.

**Available Data:**
- Topic: {topic}
- Summary: {summary}
- Image URL: {image_url}

Call the format_notion_blocks_tool() function to create properly structured Notion blocks.

Output a brief confirmation after the tool completes.""",
    tools=[format_notion_blocks_tool],
    output_key="format_status"
)
