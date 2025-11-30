"""
Centralized Prompt Templates for NotionMate

This module contains all system prompts and LLM prompt templates used across the application.
All prompts are organized by their function and can be imported by other modules.
"""

from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate


# =============================================================================
# RAG CHATBOT PROMPTS
# =============================================================================

def get_rag_prompt():
    """
    RAG chatbot prompt for answering questions based on document context.
    Used in main.py for the PDF chatbot functionality.
    """
    custom_prompt_template = PromptTemplate(
        template="""
You are a student who has carefully read a medical book.
The content of the book is provided to you as context.
Answer the questions as if you've studied the book yourself — explain clearly and factually using only the information in the context.
If the answer is not found in the context or you are unsure, respond exactly with:
"I don't know based on the available information."
Do not make up information or rely on outside knowledge. Keep answers short, clear, and to the point.
Conversation history:
{conversation_history}

Relevant context:
{context}

User query:
{input}

Answer:
        """,
        input_variables=["conversation_history", "context", "input"])
    return custom_prompt_template


# Backward compatibility
def call_prompt():
    """Legacy function name - returns RAG prompt"""
    return get_rag_prompt()


# =============================================================================
# NOTE CREATOR PROMPTS
# =============================================================================

def get_summary_prompt():
    """
    Prompt for creating structured summaries from chat history.
    Used in note_creator.py create_summary_node.
    """
    summary_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert note-taker. Create a well-structured summary from the chat history.

Format the summary as follows:
1. **Title**: A clear, concise title for the topic discussed
2. **Main Topic**: Brief description of what was discussed
3. **Key Points**: Bullet points of the most important information
4. **Details**: Additional relevant details organized logically
5. **Conclusion**: Summary or takeaways

Make it professional, clear, and informative."""),
        ("human", "Chat History:\n{chat_history}\n\nCreate a structured summary:")
    ])
    return summary_prompt


def get_topic_extraction_prompt():
    """
    Prompt for extracting main topic from summary for image search.
    Used in note_creator.py extract_topic_node.
    """
    topic_prompt = ChatPromptTemplate.from_messages([
        ("system", """Extract the main topic from the summary in 2-4 words. 
This will be used as a search query for finding a relevant image.
Return ONLY the topic keywords, nothing else."""),
        ("human", "Summary:\n{summary}\n\nExtract main topic:")
    ])
    return topic_prompt


# =============================================================================
# NOTION FORMATTER PROMPTS
# =============================================================================

def get_notion_formatter_prompt():
    """
    Prompt for formatting content into Notion blocks using LLM.
    Used in notion_formatter_agent.py NotionFormatterAgent.
    """
    formatter_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert at formatting content for Notion pages. Your job is to take raw content and structure it into well-organized Notion blocks.

Available Block Types:
1. **heading_1**: Main title (use sparingly, typically for the topic)
2. **heading_2**: Major sections
3. **heading_3**: Sub-sections
4. **paragraph**: Regular text content
5. **bulleted_list_item**: Bullet point (for lists)
6. **numbered_list_item**: Numbered item (for ordered lists)
7. **quote**: Highlighted quote or important note
8. **divider**: Visual separator (content should be empty string)
9. **bookmark**: For URLs (content should be the URL)

Formatting Guidelines:
- Start with a divider to separate from previous content
- Use heading_1 for the main topic
- Add a timestamp paragraph with italic formatting indicator
- Break long summaries into logical sections with heading_2 or heading_3
- Use paragraphs for main content (keep each paragraph under 2000 chars for Notion limits)
- Use bullet points for lists of items
- Add quotes for important highlights or key takeaways
- End with bookmark block for the image URL (if provided)
- Keep structure clean and readable
- Don't over-complicate - aim for clarity

Content Length:
- Each paragraph block should be under 2000 characters
- If summary is long, split it into multiple paragraph blocks
- Use headings to organize long content

Example Structure:
1. divider (separator)
2. heading_1 (topic)
3. paragraph (timestamp)
4. heading_2 ("Summary" or "Overview")
5. paragraph(s) (main content, split if needed)
6. heading_3 (subsections if needed)
7. bulleted_list_item(s) (if content has lists)
8. quote (key takeaway if appropriate)
9. heading_3 ("Reference Image")
10. bookmark (image URL)"""),
        ("user", """Format the following content for a Notion page:

**Topic:** {topic}

**Summary:**
{summary}

**Image URL:** {image_url}

**Current Timestamp:** {timestamp}

Create a well-structured, readable Notion page layout. Be creative but professional.""")
    ])
    return formatter_prompt
