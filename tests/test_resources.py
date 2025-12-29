import json

from fastmcp import FastMCP

from mcp_server.resources.example_resources import register_example_resources


class TestServerInfoResource:
    def test_server_info_returns_valid_json(self) -> None:
        mcp = FastMCP("test")
        register_example_resources(mcp)

        get_server_info = None
        for resource in mcp._resource_manager._resources.values():
            if "server" in str(resource.uri):
                get_server_info = resource.fn
                break

        assert get_server_info is not None
        result = get_server_info()
        data = json.loads(result)
        assert "name" in data
        assert "version" in data
        assert "status" in data

    def test_server_info_status_is_running(self) -> None:
        mcp = FastMCP("test")
        register_example_resources(mcp)

        get_server_info = None
        for resource in mcp._resource_manager._resources.values():
            if "server" in str(resource.uri):
                get_server_info = resource.fn
                break

        assert get_server_info is not None
        result = get_server_info()
        data = json.loads(result)
        assert data["status"] == "running"


class TestCapabilitiesResource:
    def test_capabilities_returns_valid_json(self) -> None:
        mcp = FastMCP("test")
        register_example_resources(mcp)

        get_capabilities = None
        for resource in mcp._resource_manager._resources.values():
            if "capabilities" in str(resource.uri):
                get_capabilities = resource.fn
                break

        assert get_capabilities is not None
        result = get_capabilities()
        data = json.loads(result)
        assert data["tools"] is True
        assert data["resources"] is True
        assert data["prompts"] is True


class TestItemResource:
    def test_get_item_returns_valid_json(self) -> None:
        mcp = FastMCP("test")
        register_example_resources(mcp)

        get_item = None
        for template in mcp._resource_manager._templates.values():
            if "items" in str(template.uri_template):
                get_item = template.fn
                break

        assert get_item is not None
        result = get_item(item_id="123")
        data = json.loads(result)
        assert data["id"] == "123"
        assert "name" in data
        assert "description" in data
