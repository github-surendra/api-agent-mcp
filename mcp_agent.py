"""
MCP Agent - Connects to MCP server and uses Anthropic Claude to reason and call tools
"""
import asyncio
import json
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
load_dotenv()  # Add this at the top

from anthropic import Anthropic

ANTHROPIC_CLIENT = Anthropic()
MODEL = "claude-opus-4-5"


class MCPAgent:
    def __init__(self):
        self.session: ClientSession | None = None
        self.tools: list = []

    async def connect(self, server_script: str):
        """Connect to MCP server"""
        server_params = StdioServerParameters(
            command="python",
            args=[server_script],
        )
        self._streams_context = stdio_client(server_params)
        streams = await self._streams_context.__aenter__()

        self._session_context = ClientSession(*streams)
        self.session = await self._session_context.__aenter__()
        await self.session.initialize()

        # Fetch available tools from MCP server
        response = await self.session.list_tools()
        self.tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            }
            for tool in response.tools
        ]
        print(f"[Agent] Connected. Available tools: {[t['name'] for t in self.tools]}")

    async def run(self, user_query: str) -> str:
        """Run agentic loop: reason → call tools → synthesize answer"""
        if not self.session:
            raise RuntimeError("Agent not connected to MCP server")

        messages = [{"role": "user", "content": user_query}]

        while True:
            response = ANTHROPIC_CLIENT.messages.create(
                model=MODEL,
                max_tokens=4096,
                tools=self.tools,
                messages=messages,
            )

            # Add assistant response to message history
            messages.append({"role": "assistant", "content": response.content})

            # If Claude is done (no more tool calls), return final answer
            if response.stop_reason == "end_turn":
                final_text = [b.text for b in response.content if hasattr(b, "text")]
                return "\n".join(final_text)

            # Process tool calls
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"[Agent] Calling tool: {block.name} with {block.input}")
                    result = await self.session.call_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result.content[0].text if result.content else "",
                    })

            if tool_results:
                messages.append({"role": "user", "content": tool_results})
            else:
                # No tool calls and no end_turn — safety exit
                break

        return "Agent completed without a final answer."

    async def disconnect(self):
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._streams_context:
            await self._streams_context.__aexit__(None, None, None)


async def run_agent(query: str) -> str:
    agent = MCPAgent()
    try:
        await agent.connect("mcp_server.py")
        result = await agent.run(query)
        return result
    finally:
        await agent.disconnect()


if __name__ == "__main__":
    query = "What is the weather in San Francisco and what is 25 * 48?"
    result = asyncio.run(run_agent(query))
    print("\n[Final Answer]\n", result)