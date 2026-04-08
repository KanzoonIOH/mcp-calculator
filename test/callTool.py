import asyncio

from fastmcp import Client

client = Client("http://localhost:8000/mcp")


async def call_tool(a: float, b: float):
    async with client:
        result = await client.call_tool("multiplication", {"a": a, "b": b})
        print(result)


async def simulate_n8n_call():
    """Simulate what n8n's AI Agent node sends: real args mixed with extra metadata."""
    async with client:
        result = await client.call_tool(
            "division",
            {
                "sessionId": "38d516d11aff472d8590654b072a1c99",
                "action": "sendMessage",
                "chatInput": "9/3",
                "a": 9,
                "b": 3,
                "tool": "division",
                "toolCallId": "chatcmpl-tool-3a962d8ff2b542c798b0d5c677d1455d",
            },
        )
        print(result)


# asyncio.run(call_tool(9, 7))
asyncio.run(simulate_n8n_call())
