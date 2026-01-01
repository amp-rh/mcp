from fastmcp import FastMCP


def register_testing_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="meta.testing.greet")
    def greet(name: str) -> str:
        """Generate a greeting for the given name."""
        return f"Hello, {name}!"

    @mcp.tool(name="meta.testing.calculate_sum")
    def calculate_sum(numbers: list[int]) -> int:
        """Calculate the sum of a list of numbers."""
        return sum(numbers)

    @mcp.tool(name="meta.testing.reverse_string")
    def reverse_string(text: str) -> str:
        """Reverse the given text string."""
        return text[::-1]
