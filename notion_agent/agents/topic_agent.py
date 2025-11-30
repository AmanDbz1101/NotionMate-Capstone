"""
Topic Agent

Extracts a concise 2-4 word topic from the summary.
"""

from google.adk.agents import LlmAgent


GEMINI_MODEL = "gemini-2.0-flash"


topic_agent = LlmAgent(
    name="TopicAgent",
    model=GEMINI_MODEL,
    description="Extracts a concise 2-4 word topic from the summary",
    instruction="""You are a Topic Extraction Agent.
Based *only* on the summary below, extract the main topic.

**Summary:**
{summary}

Extract a concise topic that is 2-4 words maximum and works well as an image search query.

Output *only* the topic (2-4 words).""",
    output_key="topic"
)
