"""
Summary Agent

Creates a structured summary from chat conversation history.
"""

from google.adk.agents import LlmAgent


GEMINI_MODEL = "gemini-2.0-flash"


summary_agent = LlmAgent(
    name="SummaryAgent",
    model=GEMINI_MODEL,
    description="Creates a structured summary from chat conversation history",
    instruction="""You are a Summary Agent.
Based *only* on the chat history below, create a well-structured, comprehensive summary.

**Chat History:**
{chat_history}

Create a summary that captures all key points, important details, and maintains logical flow.

Output *only* the summary text.""",
    output_key="summary"
)
