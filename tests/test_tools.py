from fastmcp import FastMCP

from mcp_server.tools.example_tools import register_example_tools


class TestGreetTool:
    def test_greet_returns_greeting(self) -> None:
        mcp = FastMCP("test")
        register_example_tools(mcp)

        greet = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "greet":
                greet = tool.fn
                break

        assert greet is not None
        result = greet(name="World")
        assert result == "Hello, World!"

    def test_greet_with_different_name(self) -> None:
        mcp = FastMCP("test")
        register_example_tools(mcp)

        greet = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "greet":
                greet = tool.fn
                break

        assert greet is not None
        result = greet(name="Alice")
        assert result == "Hello, Alice!"


class TestCalculateSumTool:
    def test_calculate_sum_with_numbers(self) -> None:
        mcp = FastMCP("test")
        register_example_tools(mcp)

        calculate_sum = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "calculate_sum":
                calculate_sum = tool.fn
                break

        assert calculate_sum is not None
        result = calculate_sum(numbers=[1, 2, 3, 4, 5])
        assert result == 15

    def test_calculate_sum_empty_list(self) -> None:
        mcp = FastMCP("test")
        register_example_tools(mcp)

        calculate_sum = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "calculate_sum":
                calculate_sum = tool.fn
                break

        assert calculate_sum is not None
        result = calculate_sum(numbers=[])
        assert result == 0


class TestReverseStringTool:
    def test_reverse_string(self) -> None:
        mcp = FastMCP("test")
        register_example_tools(mcp)

        reverse_string = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "reverse_string":
                reverse_string = tool.fn
                break

        assert reverse_string is not None
        result = reverse_string(text="hello")
        assert result == "olleh"

    def test_reverse_string_empty(self) -> None:
        mcp = FastMCP("test")
        register_example_tools(mcp)

        reverse_string = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "reverse_string":
                reverse_string = tool.fn
                break

        assert reverse_string is not None
        result = reverse_string(text="")
        assert result == ""

