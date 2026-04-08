import asyncio

from fastmcp import Client

client = Client("http://localhost:8000/mcp")


async def call_tool(a: float, b: float):
    async with client:
        result = await client.call_tool("multiplication", {"a": a, "b": b})
        print(result)


asyncio.run(call_tool(9, 7))
