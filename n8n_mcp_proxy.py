#!/usr/bin/env python3
"""
Simple HTTP proxy that adds authentication headers for n8n MCP server.

This proxy sits between the MCP router and n8n, adding the required
Bearer token and Accept headers that n8n's MCP server requires.
"""

import http.server
import http.client
import urllib.parse
from typing import Any

# n8n MCP configuration
N8N_HOST = "127.0.0.1"
N8N_PORT = 8080
N8N_PATH = "/mcp-server/http"
N8N_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2MTA1Y2U4Yi04NzBiLTRkZGItYjRhMS05NDE1ZjAxMTgxZWIiLCJpc3MiOiJuOG4iLCJhdWQiOiJtY3Atc2VydmVyLWFwaSIsImp0aSI6ImRkOTI1MjcyLTU5ZjEtNDQwMS05ZDdkLTdlMjgxMmViZjMyYSIsImlhdCI6MTc2NzMwMjQyM30.OuD6Q2HmrkggT6LT7jdFUzj07sZfIPwW7tpFDmgqfwE"

# Proxy configuration
PROXY_PORT = 9000


class N8nMCPProxyHandler(http.server.BaseHTTPRequestHandler):
    """Proxy handler that forwards requests to n8n with authentication."""

    def do_POST(self) -> None:
        """Handle POST requests by forwarding to n8n with auth headers."""
        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        # Create connection to n8n
        conn = http.client.HTTPConnection(N8N_HOST, N8N_PORT, timeout=30)

        try:
            # Prepare headers - forward existing headers and add authentication
            headers = {
                "Authorization": f"Bearer {N8N_TOKEN}",
                "Accept": "application/json, text/event-stream",
                "Content-Type": self.headers.get("Content-Type", "application/json"),
            }

            # Forward User-Agent if present
            if "User-Agent" in self.headers:
                headers["User-Agent"] = self.headers["User-Agent"]

            # Make request to n8n
            conn.request("POST", N8N_PATH, body, headers)
            response = conn.getresponse()

            # Send response back to client
            self.send_response(response.status)

            # Forward response headers
            for header, value in response.getheaders():
                self.send_header(header, value)
            self.end_headers()

            # Stream response body
            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                self.wfile.write(chunk)

        except Exception as e:
            # Handle errors
            self.send_error(502, f"Bad Gateway: {str(e)}")
        finally:
            conn.close()

    def do_GET(self) -> None:
        """Handle GET requests by forwarding to n8n with auth headers."""
        conn = http.client.HTTPConnection(N8N_HOST, N8N_PORT, timeout=30)

        try:
            headers = {
                "Authorization": f"Bearer {N8N_TOKEN}",
                "Accept": "application/json, text/event-stream",
            }

            # Forward User-Agent if present
            if "User-Agent" in self.headers:
                headers["User-Agent"] = self.headers["User-Agent"]

            # Forward path and query string
            path = self.path if self.path != "/" else N8N_PATH

            conn.request("GET", path, headers=headers)
            response = conn.getresponse()

            self.send_response(response.status)
            for header, value in response.getheaders():
                self.send_header(header, value)
            self.end_headers()

            # Stream response body
            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                self.wfile.write(chunk)

        except Exception as e:
            self.send_error(502, f"Bad Gateway: {str(e)}")
        finally:
            conn.close()

    def do_HEAD(self) -> None:
        """Handle HEAD requests for auth discovery."""
        conn = http.client.HTTPConnection(N8N_HOST, N8N_PORT, timeout=5)

        try:
            headers = {
                "Authorization": f"Bearer {N8N_TOKEN}",
                "Accept": "application/json, text/event-stream",
            }

            conn.request("HEAD", N8N_PATH, headers=headers)
            response = conn.getresponse()

            self.send_response(response.status)
            for header, value in response.getheaders():
                self.send_header(header, value)
            self.end_headers()

        except Exception as e:
            self.send_error(502, f"Bad Gateway: {str(e)}")
        finally:
            conn.close()

    def log_message(self, format: str, *args: Any) -> None:
        """Log requests to stdout."""
        print(f"[n8n-mcp-proxy] {self.address_string()} - {format % args}")


def run_proxy() -> None:
    """Run the proxy server."""
    server = http.server.HTTPServer(("127.0.0.1", PROXY_PORT), N8nMCPProxyHandler)
    print(f"n8n MCP Proxy running on http://127.0.0.1:{PROXY_PORT}")
    print(f"Forwarding to n8n at http://{N8N_HOST}:{N8N_PORT}{N8N_PATH}")
    print("Press Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nProxy stopped")
        server.shutdown()


if __name__ == "__main__":
    run_proxy()
