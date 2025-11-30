"""
Notion Writer Tool

Writes formatted blocks to Notion pages using MCP tools.
"""

import asyncio
import json
from google.adk.tools.tool_context import ToolContext
from langchain_mcp_adapters.client import MultiServerMCPClient
from notion_mcp_config import SERVERS


def write_to_notion_tool(tool_context: ToolContext) -> str:
    """Write formatted blocks to Notion page using MCP tools"""
    notion_blocks = tool_context.state.get("notion_blocks", [])
    notion_page_id = tool_context.state.get("notion_page_id")
    
    if not notion_blocks:
        error_msg = "No Notion blocks available for writing"
        tool_context.state["notion_write_success"] = False
        return error_msg
    
    async def write_async():
        try:
            # Initialize MCP client
            client = MultiServerMCPClient(SERVERS)
            tools = await client.get_tools()
            
            # Find tools
            search_tool = next((t for t in tools if "search" in t.name.lower()), None)
            append_blocks_tool = next((t for t in tools if "patch-block-children" in t.name.lower()), None)
            
            if not append_blocks_tool:
                return {"success": False, "error": "Append blocks tool not found in MCP"}
            
            # Get page if not provided
            target_page_id = notion_page_id
            page_title = "Specified Page"
            
            if not target_page_id:
                if not search_tool:
                    return {"success": False, "error": "Search tool not found in MCP"}
                
                # Get first available page
                search_result = await search_tool.ainvoke({"query": ""})
                result_str = str(search_result)
                
                if '"results":[' in result_str:
                    json_start = result_str.find('{"object":')
                    json_end = result_str.rfind('}') + 1
                    if json_start != -1 and json_end > json_start:
                        results_json = json.loads(result_str[json_start:json_end])
                        if 'results' in results_json and len(results_json['results']) > 0:
                            first_result = results_json['results'][0]
                            target_page_id = first_result.get('id')
                            page_title = "Untitled"
                            
                            if 'properties' in first_result:
                                props = first_result['properties']
                                for prop_name, prop_value in props.items():
                                    if prop_value.get('type') == 'title':
                                        title_array = prop_value.get('title', [])
                                        if title_array and len(title_array) > 0:
                                            page_title = title_array[0].get('plain_text', 'Untitled')
                                            break
                        else:
                            return {"success": False, "error": "No pages found in Notion workspace"}
                else:
                    return {"success": False, "error": "No pages found in Notion workspace"}
            
            # Write blocks
            await append_blocks_tool.ainvoke({
                "block_id": target_page_id,
                "children": notion_blocks
            })
            
            return {
                "success": True,
                "page_id": target_page_id,
                "page_title": page_title
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Run async function with nest_asyncio support
    try:
        result = asyncio.run(write_async())
        
        if result["success"]:
            tool_context.state["notion_write_success"] = True
            tool_context.state["notion_page_title"] = result["page_title"]
            return f"Successfully written to Notion page: '{result['page_title']}'"
        else:
            tool_context.state["notion_write_success"] = False
            return f"Failed to write to Notion: {result['error']}"
    
    except Exception as e:
        tool_context.state["notion_write_success"] = False
        return f"Error writing to Notion: {str(e)}"
