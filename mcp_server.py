"""
MCP Server - Provides tools that agents can call
"""
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import json
import httpx

app = Server("mcp-demo-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_web",
            description="Search the web for information on a given topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_weather",
            description="Get current weather for a city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                },
                "required": ["city"],
            },
        ),
        Tool(
            name="calculate",
            description="Perform a mathematical calculation",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression to evaluate"},
                },
                "required": ["expression"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "search_web":
        query = arguments["query"]
        # Simulated search result
        result = {
            "query": query,
            "results": [
                {"title": f"Result 1 for '{query}'", "snippet": f"This is a relevant snippet about {query}."},
                {"title": f"Result 2 for '{query}'", "snippet": f"Another relevant result about {query}."},
            ],
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "get_weather":
        city = arguments["city"]
        # Simulated weather data
        result = {
            "city": city,
            "temperature": "72°F",
            "condition": "Partly Cloudy",
            "humidity": "55%",
            "wind": "10 mph",
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "calculate":
        expression = arguments["expression"]
        try:
            # Safe evaluation of math expressions
            allowed = {k: v for k, v in __builtins__.items()
                       if k in ["abs", "round", "min", "max", "sum", "pow"]} if isinstance(__builtins__, dict) else {}
            result = eval(expression, {"__builtins__": allowed})
            return [TextContent(type="text", text=json.dumps({"expression": expression, "result": result}))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())