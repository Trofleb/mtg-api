"""MTG MCP Server - FastMCP server for MTG card and rules data."""

import os

from fastapi import FastAPI
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(
    name="MTG MCP Server",
    instructions=(
        "This server provides access to Magic: The Gathering (MTG) card data "
        "and comprehensive rules through the Model Context Protocol. "
        "Use tools to search for cards and query rules. "
        "Use resources to access specific cards by ID and set information."
    ),
)

# Import resources to register them with the MCP server
# Resources auto-register via @mcp.resource() decorators
from mcp_server.resources import cards  # noqa: E402, F401

# Create a FastAPI app for health checks
# FastMCP uses this internally for HTTP/SSE transport
app = FastAPI()


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint for Docker container monitoring.

    Returns:
        Status dictionary with "status": "ok"
    """
    return {"status": "ok"}


# Mount health check to MCP app
# This allows the Docker healthcheck to work while MCP handles /mcp endpoint
if hasattr(mcp, "_fastapi_app"):
    mcp._fastapi_app.mount("/health", app)


def main() -> None:
    """Run the MCP server with HTTP/SSE transport.

    Configuration from environment variables:
    - MCP_HOST: Host to bind to (default: 0.0.0.0)
    - MCP_PORT: Port to listen on (default: 8002)
    - API_BASE_URL: FastAPI backend URL (default: http://localhost:8000)
    """
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8002"))

    print(f"Starting MTG MCP Server on {host}:{port}")
    print(f"API Backend: {os.getenv('API_BASE_URL', 'http://localhost:8000')}")

    # Run with HTTP/SSE transport for remote access
    mcp.run(
        transport="streamable-http",  # Server-Sent Events for streaming
        host=host,
        port=port,
    )


if __name__ == "__main__":
    main()
