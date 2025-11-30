"""
Image Search Agent

Searches for a relevant image based on the extracted topic.
"""

from google.adk.agents import LlmAgent
from ..tools.image_search_tool import search_image_from_state_tool


GEMINI_MODEL = "gemini-2.0-flash"


image_search_agent = LlmAgent(
    name="ImageSearchAgent",
    model=GEMINI_MODEL,
    description="Searches for a relevant image based on the extracted topic",
    instruction="""You are an Image Search Agent.
You have access to the 'search_image_from_state_tool' function.

**Topic:**
{topic}

Call the search_image_from_state_tool() function to search for an appropriate image.

Output a brief confirmation after the tool completes.""",
    tools=[search_image_from_state_tool],
    output_key="image_search_status"
)
