"""
Notion Writer Agent

Writes the formatted Notion blocks to a Notion page.
"""

from google.adk.agents import LlmAgent
from ..tools.notion_writer_tool import write_to_notion_tool


GEMINI_MODEL = "gemini-2.0-flash"


writer_agent = LlmAgent(
    name="NotionWriterAgent",
    model=GEMINI_MODEL,
    description="Writes the formatted Notion blocks to a Notion page",
    instruction="""You are a Notion Writer Agent.
You have access to the 'write_to_notion_tool' function.

**Target Page ID (if specified):**
{notion_page_id}

Call the write_to_notion_tool() function to write the blocks to Notion.

Output a final confirmation with the write status.""",
    tools=[write_to_notion_tool],
    output_key="write_status"
)
