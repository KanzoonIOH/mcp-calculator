from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict

from tools.calculator import add, devide, multiply, substract

mcp = FastMCP(name="calculator")


# ── INPUT MODEL ───────────────────────────────────────────────────────────────
# extra="ignore" silently discards any unexpected fields that some LLM clients
# (e.g. n8n + Qwen) inject into tool call arguments (sessionId, chatInput, etc.)


class CalcInput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    a: float
    b: float


# ── TOOL ──────────────────────────────────────────────────────────────────────
# A function the AI calls to *do something*.
# The agent decides when to invoke it based on the user's request.


@mcp.tool()
def addition(input: CalcInput) -> float:
    """
    Add two numbers together.
    Use this when you need to sum two values.
    """
    return add(input.a, input.b)


@mcp.tool()
def subtraction(input: CalcInput) -> float:
    """
    Subtract b from a and return the result.
    Use this when you need to find the difference between two values.
    """
    return substract(input.a, input.b)


@mcp.tool()
def multiplication(input: CalcInput) -> float:
    """
    Multiply two numbers and return the result.
    Use this when you need to find the product of two values.
    """
    return multiply(input.a, input.b)


@mcp.tool()
def division(input: CalcInput) -> float:
    """
    Divide a by b and return the result.
    Use this when you need to find the quotient of two values.
    Raises an error if b is zero.
    """
    return devide(input.a, input.b)


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
    mcp.run(transport="sse")
