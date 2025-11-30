"""
Image Search Tool

Searches for relevant images using Serper API based on topic.
"""

import os
import requests
from google.adk.tools.tool_context import ToolContext


def search_image_tool(query: str) -> str:
    """Search for one image using Serper API"""
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")
    
    if not SERPER_API_KEY:
        return "No API key found"
    
    url = "https://google.serper.dev/images"
    payload = {"q": query, "num": 1}
    headers = {"X-API-KEY": SERPER_API_KEY}

    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        
        if "images" in data and data["images"]:
            return data["images"][0]["imageUrl"]
        else:
            return "No image found"
    except Exception as e:
        return f"Error searching image: {str(e)}"


def search_image_from_state_tool(tool_context: ToolContext) -> str:
    """Search for image based on topic in session state"""
    topic = tool_context.state.get("topic", "")
    
    if not topic:
        error_msg = "No topic available for image search"
        tool_context.state["image_url"] = ""
        return error_msg
    
    # Search for image
    image_url = search_image_tool(topic)
    
    # Store in session state
    tool_context.state["image_url"] = image_url
    
    return f"Image found: {image_url}"
