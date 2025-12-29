from fastmcp import FastMCP


def register_example_tools(mcp: FastMCP) -> None:
    @mcp.tool
    def greet(name: str) -> str:
        """Generate a greeting for the given name."""
        return f"Hello, {name}!"

    @mcp.tool
    def calculate_sum(numbers: list[int]) -> int:
        """Calculate the sum of a list of numbers."""
        return sum(numbers)

    @mcp.tool
    def reverse_string(text: str) -> str:
        """Reverse the given text string."""
        return text[::-1]

