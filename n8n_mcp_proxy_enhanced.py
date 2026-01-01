#!/usr/bin/env python3
"""
Enhanced HTTP proxy that translates REST endpoints to n8n's JSON-RPC MCP server.

This proxy sits between the MCP router and n8n, translating:
- REST-style requests (GET /tools, POST /tools/call)
- To JSON-RPC over SSE (n8n's MCP protocol)
"""

import http.server
import http.client
import json
from typing import Any
from urllib.parse import parse_qs, urlparse

# n8n MCP configuration
N8N_HOST = "127.0.0.1"
N8N_PORT = 8080
N8N_PATH = "/mcp-server/http"
N8N_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2MTA1Y2U4Yi04NzBiLTRkZGItYjRhMS05NDE1ZjAxMTgxZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJtY3Atc2VydmVyLWFwaSIsImp0aSI6ImRkOTI1MjcyLTU5ZjEtNDQwMS05ZDdkLTdlMjgxMmViZjMyYSIsImlhdCI6MTc2NzMwMjQyM30.OuD6Q2HmrkggT6LT7jdFUzj07sZfIPwW7tpFDmgqfwE"

# Proxy configuration
PROXY_PORT = 9000


class N8nMCPProxyHandler(http.server.BaseHTTPRequestHandler):
    """Proxy handler that translates REST to JSON-RPC for n8n MCP."""

    request_counter = 0

    def translate_rest_to_jsonrpc(self, method: str, path: str, body: bytes) -> dict:
        """Translate REST endpoint to JSON-RPC request."""
        N8nMCPProxyHandler.request_counter += 1
        request_id = N8nMCPProxyHandler.request_counter

        # Parse path
        parsed = urlparse(path)
        path_parts = parsed.path.strip("/").split("/")

        # Handle different endpoint patterns
        if path == "/tools" or path == "/tools/":
            # GET /tools -> tools/list
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "tools/list",
                "params": {}
            }

        elif path.startswith("/tools/list"):
            # POST /tools/list -> tools/list
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "tools/list",
                "params": {}
            }

        elif path.startswith("/tools/call"):
            # POST /tools/call -> tools/call
            try:
                data = json.loads(body) if body else {}
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "method": "tools/call",
                    "params": {
                        "name": data.get("name", ""),
                        "arguments": data.get("arguments", {})
                    }
                }
            except json.JSONDecodeError:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "method": "tools/call",
                    "params": {}
                }

        elif path == "/resources" or path == "/resources/":
            # GET /resources -> resources/list
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "resources/list",
                "params": {}
            }

        elif path.startswith("/resources/list"):
            # POST /resources/list -> resources/list
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "resources/list",
                "params": {}
            }

        elif path == "/prompts" or path == "/prompts/":
            # GET /prompts -> prompts/list
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "prompts/list",
                "params": {}
            }

        elif path.startswith("/prompts/list"):
            # POST /prompts/list -> prompts/list
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "prompts/list",
                "params": {}
            }

        # Default: pass through as initialize or return error
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "mcp-router", "version": "1.0"}
            }
        }

    def parse_sse_response(self, sse_data: str) -> dict:
        """Parse SSE format response to extract JSON data."""
        lines = sse_data.strip().split("\n")
        for line in lines:
            if line.startswith("data: "):
                json_str = line[6:]  # Remove "data: " prefix
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    continue
        return {}

    def forward_to_n8n(self, jsonrpc_request: dict) -> tuple[int, dict]:
        """Forward JSON-RPC request to n8n and parse response."""
        conn = http.client.HTTPConnection(N8N_HOST, N8N_PORT, timeout=30)

        try:
            headers = {
                "Authorization": f"Bearer {N8N_TOKEN}",
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json"
            }

            body = json.dumps(jsonrpc_request).encode()
            conn.request("POST", N8N_PATH, body, headers)
            response = conn.getresponse()

            # Read the full response
            response_data = response.read().decode()

            # Parse SSE response
            result = self.parse_sse_response(response_data)

            return response.status, result

        except Exception as e:
            return 502, {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Proxy error: {str(e)}"
                },
                "id": jsonrpc_request.get("id")
            }
        finally:
            conn.close()

    def do_GET(self) -> None:
        """Handle GET requests by translating to JSON-RPC."""
        # Translate REST endpoint to JSON-RPC
        jsonrpc_request = self.translate_rest_to_jsonrpc("GET", self.path, b"")

        # Forward to n8n
        status, result = self.forward_to_n8n(jsonrpc_request)

        # Send response
        self.send_response(200 if status == 200 else status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        # Format response for REST client
        if "result" in result:
            response_data = result["result"]
        elif "error" in result:
            response_data = {"error": result["error"]}
        else:
            response_data = result

        self.wfile.write(json.dumps(response_data).encode())

    def do_POST(self) -> None:
        """Handle POST requests by translating to JSON-RPC."""
        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        # Translate REST endpoint to JSON-RPC
        jsonrpc_request = self.translate_rest_to_jsonrpc("POST", self.path, body)

        # Forward to n8n
        status, result = self.forward_to_n8n(jsonrpc_request)

        # Send response
        self.send_response(200 if status == 200 else status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        # Format response for REST client
        if "result" in result:
            response_data = result["result"]
        elif "error" in result:
            response_data = {"error": result["error"]}
        else:
            response_data = result

        self.wfile.write(json.dumps(response_data).encode())

    def do_HEAD(self) -> None:
        """Handle HEAD requests for health checks."""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        """Log requests to stdout."""
        print(f"[n8n-mcp-proxy] {self.address_string()} - {format % args}")


def run_proxy() -> None:
    """Run the enhanced proxy server."""
    server = http.server.HTTPServer(("127.0.0.1", PROXY_PORT), N8nMCPProxyHandler)
    print(f"Enhanced n8n MCP Proxy running on http://127.0.0.1:{PROXY_PORT}")
    print(f"Forwarding to n8n at http://{N8N_HOST}:{N8N_PORT}{N8N_PATH}")
    print("Translating REST endpoints to JSON-RPC")
    print("Press Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nProxy stopped")
        server.shutdown()


if __name__ == "__main__":
    run_proxy()
