"""
Notion Formatter Agent

Uses LLM to intelligently format content into Notion blocks.
Takes topic, summary, and image URL and generates well-structured Notion blocks.
"""

import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from datetime import datetime
from rag_component.prompt import get_notion_formatter_prompt

load_dotenv()


# ============================================================================
# Pydantic Models for Structured LLM Outputs
# ============================================================================

class NotionBlock(BaseModel):
    """
    Single Notion block with type and content.
    
    Used by NotionFormatterAgent to structure LLM output into Notion-compatible blocks.
    """
    block_type: str = Field(
        description="Type of block: heading_1, heading_2, heading_3, paragraph, "
                    "bulleted_list_item, numbered_list_item, quote, divider, bookmark"
    )
    content: str = Field(
        description="Text content for the block (empty string for divider)"
    )


class NotionFormatting(BaseModel):
    """
    Complete Notion formatting result from LLM.
    
    Contains a list of NotionBlock objects and reasoning for the formatting decisions.
    """
    blocks: List[NotionBlock] = Field(
        description="List of Notion blocks to create"
    )
    reasoning: str = Field(
        description="Brief explanation of the formatting decisions"
    )


class NotionFormatterAgent:
    """
    Agent that uses LLM to format content into well-structured Notion blocks.
    """
    
    def __init__(self):
        """Initialize the formatter with Groq LLM."""
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",  # Use Llama 3.3 70B for better formatting
            temperature=0.3,  # Some creativity for formatting decisions
            api_key=os.environ.get("GROQ_API_KEY")
        )
        
        # Create structured output LLM
        self.structured_llm = self.llm.with_structured_output(NotionFormatting)
        
        # Get prompt from centralized prompts module
        self.prompt = get_notion_formatter_prompt()
        
        # Create the formatting chain
        self.chain = self.prompt | self.structured_llm
    
    def format_content(
        self,
        topic: str,
        summary: str,
        image_url: Optional[str] = None
    ) -> NotionFormatting:
        """
        Format content into Notion blocks using LLM.
        
        Args:
            topic: The main topic/title
            summary: The content summary
            image_url: Optional image URL
            
        Returns:
            NotionFormatting with blocks and reasoning
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            result = self.chain.invoke({
                "topic": topic,
                "summary": summary,
                "image_url": image_url if image_url and image_url != "No image found" else "None",
                "timestamp": timestamp
            })
            
            return result
            
        except Exception as e:
            # Fallback to basic formatting
            return self._create_fallback_blocks(topic, summary, image_url, timestamp)
    
    def _create_fallback_blocks(
        self,
        topic: str,
        summary: str,
        image_url: Optional[str],
        timestamp: str
    ) -> NotionFormatting:
        """Create basic blocks if LLM formatting fails."""
        blocks = [
            NotionBlock(block_type="divider", content=""),
            NotionBlock(block_type="heading_1", content=topic),
            NotionBlock(block_type="paragraph", content=f"Added: {timestamp}"),
            NotionBlock(block_type="heading_2", content="Summary"),
            NotionBlock(block_type="paragraph", content=summary[:2000])
        ]
        
        if image_url and image_url != "No image found":
            blocks.append(NotionBlock(block_type="heading_3", content="Reference Image"))
            blocks.append(NotionBlock(block_type="bookmark", content=image_url))
        
        return NotionFormatting(
            blocks=blocks,
            reasoning="Fallback formatting due to error"
        )
    
    def blocks_to_notion_format(self, formatting: NotionFormatting) -> List[Dict[str, Any]]:
        """
        Convert NotionBlock objects to actual Notion API block format.
        
        Args:
            formatting: NotionFormatting object with blocks
            
        Returns:
            List of Notion API block dictionaries
        """
        notion_blocks = []
        
        for block in formatting.blocks:
            block_type = block.block_type
            content = block.content
            
            if block_type == "divider":
                notion_blocks.append({
                    "object": "block",
                    "type": "divider",
                    "divider": {}
                })
            
            elif block_type == "bookmark":
                if content and content.startswith("http"):
                    notion_blocks.append({
                        "object": "block",
                        "type": "bookmark",
                        "bookmark": {"url": content}
                    })
            
            elif block_type in ["heading_1", "heading_2", "heading_3"]:
                notion_blocks.append({
                    "object": "block",
                    "type": block_type,
                    block_type: {
                        "rich_text": [{"type": "text", "text": {"content": content[:2000]}}]
                    }
                })
            
            elif block_type == "paragraph":
                notion_blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": content[:2000]}}]
                    }
                })
            
            elif block_type == "bulleted_list_item":
                notion_blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": content[:2000]}}]
                    }
                })
            
            elif block_type == "numbered_list_item":
                notion_blocks.append({
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": content[:2000]}}]
                    }
                })
            
            elif block_type == "quote":
                notion_blocks.append({
                    "object": "block",
                    "type": "quote",
                    "quote": {
                        "rich_text": [{"type": "text", "text": {"content": content[:2000]}}]
                    }
                })
        
        return notion_blocks
