"""
Note Creation Workflow

Main workflow orchestrator that coordinates all agents to create
notes from chat history and write them to Notion.
"""

import os
import asyncio
import nest_asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from google.adk.agents import SequentialAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from dotenv import load_dotenv

# Import all agents
from .agents.summary_agent import summary_agent
from .agents.topic_agent import topic_agent
from .agents.image_search_agent import image_search_agent
from .agents.formatter_agent import formatter_agent
from .agents.writer_agent import writer_agent

# Apply nest_asyncio globally to allow nested event loops
nest_asyncio.apply()

os.environ["OTEL_SDK_DISABLED"] = "true"
load_dotenv()


# ============================================================================
# Sequential Workflow Definition
# ============================================================================

note_creation_workflow = SequentialAgent(
    name="NoteCreationWorkflow",
    sub_agents=[
        summary_agent,
        topic_agent,
        image_search_agent,
        formatter_agent,
        writer_agent
    ],
    description="Sequential workflow that creates a note from chat history and writes it to Notion"
)

root_agent = note_creation_workflow
# ============================================================================
# Main Workflow Execution Functions
# ============================================================================

async def create_note_from_history_async(
    chat_history: str, 
    notion_page_id: Optional[str] = None,
    notion_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a note from chat history and write to Notion using ADK Sequential Agents.
    
    Args:
        chat_history: Full chat history as a formatted string
        notion_page_id: Optional specific Notion page ID to write to
        notion_token: User's Notion integration token
        
    Returns:
        dict: Result containing success status, summary, topic, image_url, and Notion info
    """
    try:
        if not notion_token:
            return {
                "success": False,
                "error": "Notion token is required"
            }
        
        # Create session service
        session_service = InMemorySessionService()
        
        # Constants for session
        APP_NAME = "notionmate_app"
        USER_ID = "user_1"
        SESSION_ID = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create session with initial state
        initial_state = {
            "chat_history": chat_history,
            "notion_page_id": notion_page_id or "",
            "notion_token": notion_token
        }
        
        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID,
            state=initial_state
        )
        
        # Create runner
        runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=session_service
        )
        
        # Simple user message
        content = types.Content(
            role='user',
            parts=[types.Part(text="Process the chat history and create a Notion note.")]
        )
        
        # Process ALL events from ALL agents
        final_response = None
        
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=content
        ):
            # Store the final response but DON'T break!
            if event.is_final_response():
                final_response = event
                # Continue processing - there might be more agents!
        
        # Retrieve final session state
        final_session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )
        
        # Extract results from state
        summary = final_session.state.get('summary', '')
        topic = final_session.state.get('topic', '')
        image_url = final_session.state.get('image_url', '')
        notion_write_success = final_session.state.get('notion_write_success', False)
        notion_page_title = final_session.state.get('notion_page_title', '')
        
        return {
            "success": True,
            "summary": summary,
            "topic": topic,
            "image_url": image_url,
            "notion_write_success": notion_write_success,
            "notion_page_id": notion_page_id or "",
            "notion_page_title": notion_page_title,
            "error": ""
        }
        
    except Exception as e:
        error_msg = str(e)
        
        return {
            "success": False,
            "error": error_msg,
            "summary": "",
            "topic": "",
            "image_url": "",
            "notion_write_success": False,
            "notion_page_id": "",
            "notion_page_title": ""
        }


def create_note_from_history(
    chat_history: str, 
    notion_page_id: Optional[str] = None,
    notion_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Synchronous wrapper for create_note_from_history_async.
    
    Args:
        chat_history: Full chat history as a formatted string
        notion_page_id: Optional specific Notion page ID to write to
        notion_token: User's Notion integration token
        
    Returns:
        dict: Result containing success status and all relevant data
    """
    try:
        result = asyncio.run(create_note_from_history_async(chat_history, notion_page_id, notion_token))
        return result
    except Exception as e:
        return {
            "success": False, 
            "error": str(e),
            "summary": "",
            "topic": "",
            "image_url": "",
            "notion_write_success": False,
            "notion_page_id": "",
            "notion_page_title": ""
        }
