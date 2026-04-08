from fastmcp import FastMCP
from fastmcp.server.middleware import Middleware, MiddlewareContext

from tools.calculator import add, devide, multiply, substract


class StripExtraFieldsMiddleware(Middleware):
    """
    Strips extra fields injected by n8n's AI Agent node (sessionId, action,
    chatInput, toolCallId) before FastMCP validates the tool arguments.
    """

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        tool_name = context.message.name
        arguments = context.message.arguments or {}

        # Fetch the tool definition to get its declared parameter names
        tool = await context.fastmcp_context.fastmcp.get_tool(tool_name)
        if tool is not None:
            known_params = set(tool.parameters.get("properties", {}).keys())
            context.message.arguments = {
                k: v for k, v in arguments.items() if k in known_params
            }

        return await call_next(context)


mcp = FastMCP(name="calculator", middleware=[StripExtraFieldsMiddleware()])


# ── TOOL ──────────────────────────────────────────────────────────────────────
@mcp.tool()
def addition(a: float, b: float) -> float:
    """
    Add two numbers together.
    Use this when you need to sum two values.
    """
    return add(a, b)


@mcp.tool()
def subtraction(a: float, b: float) -> float:
    """
    Subtract b from a and return the result.
    Use this when you need to find the difference between two values.
    """
    return substract(a, b)


@mcp.tool()
def multiplication(a: float, b: float) -> float:
    """
    Multiply two numbers and return the result.
    Use this when you need to find the product of two values.
    """
    return multiply(a, b)


@mcp.tool()
def division(a: float, b: float) -> float:
    """
    Divide a by b and return the result.
    Use this when you need to find the quotient of two values.
    Raises an error if b is zero.
    """
    return devide(a, b)


# ── RESOURCE ──────────────────────────────────────────────────────────────────
# Read-only data the AI can read as background context.
# Think of it like a reference sheet the agent can look up.
# Accessed via a URI — the client fetches it, not the AI autonomously.


@mcp.resource("resource://calculator/formulas")
def get_formulas() -> str:
    """A reference sheet of supported calculator formulas."""
    return """
Supported Formulas
==================
1. Addition       : result = a + b       (tool: addition)
2. Subtraction    : result = a - b       (tool: subtraction)
3. Multiplication : result = a * b       (tool: multiplication)
4. Division       : result = a / b       (tool: division, raises error if b=0)

More formulas (credit card payment, loan EMI, etc.) will be added here.
"""


# ── PROMPT ────────────────────────────────────────────────────────────────────
# A reusable conversation starter / instruction template.
# The client (n8n, Claude, etc.) loads this to set up context before the chat.
# It tells the AI how to behave and which tools to use.


@mcp.prompt()
def calculator_assistant() -> str:
    """Sets up the AI as a calculator assistant that uses the addition tool."""
    return """
You are a calculator assistant.

When the user asks you to add numbers, use the `addition` tool to compute the result.
Always show the inputs and the result clearly, for example:
  "3 + 4 = 7"

Do not calculate in your head — always call the tool so the result is verified.
"""


if __name__ == "__main__":
    mcp.run()
