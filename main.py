import inspect

from fastmcp import FastMCP

from tools.calculator import add, devide, multiply, substract

mcp = FastMCP(name="calculator")


# ── HELPER ────────────────────────────────────────────────────────────────────
# Some LLM clients (e.g. n8n + Qwen) inject extra fields into tool call
# arguments (sessionId, chatInput, action, toolCallId, …). This decorator
# strips any keyword argument that the wrapped function does not declare,
# so Pydantic validation never sees the unexpected fields.
#
# NOTE: We intentionally do NOT use @functools.wraps here. wraps() sets
# __wrapped__, which causes Pydantic's TypeAdapter to follow the reference
# back to the original function's strict signature and reject extra keys.
# Instead we copy only the attributes FastMCP needs (__name__, __doc__,
# __annotations__), leaving the wrapper's own **kwargs signature visible
# to Pydantic so it accepts — and we discard — the unknown fields.


def ignore_extra_args(fn):
    sig = inspect.signature(fn)

    def wrapper(**kwargs):
        filtered = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return fn(**filtered)

    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    wrapper.__annotations__ = fn.__annotations__
    return wrapper


# ── TOOL ──────────────────────────────────────────────────────────────────────
@mcp.tool()
@ignore_extra_args
def addition(a: float, b: float) -> float:
    """
    Add two numbers together.
    Use this when you need to sum two values.
    """
    return add(a, b)


@mcp.tool()
@ignore_extra_args
def subtraction(a: float, b: float) -> float:
    """
    Subtract b from a and return the result.
    Use this when you need to find the difference between two values.
    """
    return substract(a, b)


@mcp.tool()
@ignore_extra_args
def multiplication(a: float, b: float) -> float:
    """
    Multiply two numbers and return the result.
    Use this when you need to find the product of two values.
    """
    return multiply(a, b)


@mcp.tool()
@ignore_extra_args
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
    mcp.run(transport="sse")
