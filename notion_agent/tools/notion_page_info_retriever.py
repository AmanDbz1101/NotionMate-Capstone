"""
Simplified Notion Writer using MCP tools directly
Searches for pages, creates/updates them without LangGraph complexity
"""

import json
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from notion_mcp_config import SERVERS

load_dotenv()


async def get_notion_pages():
    """
    Get list of all available Notion pages
    
    Returns:
        list: List of dicts with 'id' and 'title' keys
    """
    try:
        client = MultiServerMCPClient(SERVERS)
        tools = await client.get_tools()
        
        search_tool = next((t for t in tools if "search" in t.name.lower()), None)
        if not search_tool:
            return []
        
        # Search for all pages
        search_result = await search_tool.ainvoke({"query": ""})
        result_str = str(search_result)
        
        pages = []
        if '"results":[' in result_str:
            json_start = result_str.find('{"object":')
            json_end = result_str.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                results_json = json.loads(result_str[json_start:json_end])
                if 'results' in results_json:
                    for result in results_json['results']:
                        page_id = result.get('id')
                        page_title = "Untitled"
                        
                        if 'properties' in result:
                            props = result['properties']
                            for prop_name, prop_value in props.items():
                                if prop_value.get('type') == 'title':
                                    title_array = prop_value.get('title', [])
                                    if title_array and len(title_array) > 0:
                                        page_title = title_array[0].get('plain_text', 'Untitled')
                                        break
                        
                        pages.append({"id": page_id, "title": page_title})
        
        return pages
        
    except Exception as e:
        return []

