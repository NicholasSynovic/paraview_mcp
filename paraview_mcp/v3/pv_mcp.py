"""
ParaView MCP server engine (v3, single-tool execute_code).

Unlike v1/v2 (which share the tool set defined in ``paraview_mcp.tools``),
v3 defines its **own** ``FastMCP`` instance and exposes a **single** tool:
``execute_code``. Like v2 it serves over MCP streamable-http and binds to a
configurable host/port (the MCP transport address, distinct from the ParaView
server address).

Usage:
1. Start pvserver with --multi-clients (e.g. pvserver --multi-clients
   --server-port=11111).
2. Start the ParaView app and connect to the server.
3. Point an MCP streamable-http client at the bound host:port (default
   http://localhost:8080/mcp).
"""

from mcp.server.fastmcp import FastMCP

# Reuse the shared behavioral prompt and logger from the tools module. v3 does
# not import the shared tool set, only these two helpers.
from paraview_mcp.tools import default_prompt, logger

# The single FastMCP instance for the v3 engine. Distinct from the shared
# instance in ``paraview_mcp.tools`` used by v1/v2.
mcp = FastMCP("ParaView", instructions=default_prompt)


# ============================================================================
# MCP Tool for ParaView (v3)
# ============================================================================


@mcp.tool()
def execute_code(code: str) -> str:
    """
    Execute a Python code string against the ParaView server.

    Args:
        code: Python source to run on the ParaView server.

    Returns:
        Status message.
    """
    return "Hello World"


def run(
    paraview_server: str = "localhost",
    paraview_port: int = 11111,
    mcp_server: str = "localhost",
    mcp_port: int = 8080,
) -> None:
    """
    Run the v3 MCP server over streamable-http.

    CLI parsing, logging setup and ``sys.path`` handling for an external
    ParaView install are performed by ``paraview_mcp.cli`` and
    ``paraview_mcp.main`` before this function is called.

    Args:
        paraview_server: ParaView server hostname to connect to.
        paraview_port: ParaView server port to connect to.
        mcp_server: Hostname the MCP server binds to (transport), distinct
            from the ParaView server.
        mcp_port: Port the MCP server binds to (transport), distinct from the
            ParaView port.
        compress_screenshots: Whether to compress screenshots to reduce token
            usage.
        max_screenshot_width: Maximum screenshot width in pixels when
            compression is enabled (height scales proportionally).
        screenshot_quality: JPEG quality (1-100) when compression is enabled.
    """
    # Configure the MCP transport bind address before serving.
    mcp.settings.host = mcp_server
    mcp.settings.port = mcp_port

    # Run the MCP server over streamable-http using the configured bind address.
    try:
        logger.info("Starting ParaView External MCP Server")
        logger.info(f"ParaView server: {paraview_server}:{paraview_port}")
        logger.info(f"MCP server (streamable-http): {mcp_server}:{mcp_port}")
        mcp.run(transport="streamable-http")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error running MCP server: {str(e)}")
