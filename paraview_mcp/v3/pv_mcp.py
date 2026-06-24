"""
ParaView MCP server engine (v3, streamable-http transport).

Unlike v1/v2 (which share the 39-tool ``mcp`` instance from
``paraview_mcp.tools``), v3 is intentionally minimal: it defines its OWN
``FastMCP`` instance exposing a SINGLE tool, ``execute_code``. That tool ships
a Python source string to the connected ParaView server, where it is run as
the ``Script`` of a reused ``ProgrammableSource`` (executed server-side by
``UpdatePipeline()``). v3 therefore does NOT import ``paraview_mcp.tools``.

Usage:
1. Start pvserver with --multi-clients (e.g. pvserver --multi-clients
   --server-port=11111).
2. Start the ParaView app and connect to the server.
3. Point an MCP streamable-http client at the bound host:port (default
   http://localhost:8080/mcp).
"""

from mcp.server.fastmcp import FastMCP

from paraview_mcp import __prog__
from paraview_mcp.logger import setup_logging
from paraview_mcp.manager import ParaViewManager

logger = setup_logging()

# v3-specific behavioral contract sent to the LLM. The single tool runs code
# in the ProgrammableSource server-side sandbox, NOT a full paraview.simple
# session.
default_prompt = """
This ParaView interface exposes a single tool, execute_code.

execute_code runs your Python source on the ParaView server as the Script of a
ProgrammableSource. The code executes server-side in the Programmable Source
sandbox (names such as `self`, `output` and `vtk` are available); it is NOT a
full paraview.simple session, so do not expect functions like Show() or
LoadState() to be importable inside the script. Anything the script prints goes
to the pvserver process and is not returned; the tool returns only a success or
error message.
"""

# v3 owns its own single-tool FastMCP instance (it does not share the 39-tool
# instance from paraview_mcp.tools).
mcp = FastMCP(name=__prog__, instructions=default_prompt)

# The ParaView manager is constructed in run() and installed here so the tool
# function below can reference it.
pv_manager: ParaViewManager | None = None


def set_pv_manager(manager: ParaViewManager) -> None:
    """Install the ParaView manager referenced by the tool function."""
    global pv_manager
    pv_manager = manager


@mcp.tool()
def execute_code(code: str) -> str:
    """
    Execute a Python script on the connected ParaView server.

    The code is run server-side as the Script of a reused ProgrammableSource.
    It executes in the Programmable Source sandbox (e.g. ``self``, ``output``,
    ``vtk``), not a full ``paraview.simple`` session. Output printed by the
    script is not captured; this tool returns only a status message (or the
    client-side error/traceback on failure).

    Args:
        code: Python source to run on the ParaView server.

    Returns:
        Status message indicating success or failure.
    """
    _success, message = pv_manager.execute_code(code)
    return message


def run(
    paraview_server: str = "localhost",
    paraview_port: int = 11111,
    mcp_server: str = "localhost",
    mcp_port: int = 8080,
    compress_screenshots: bool = True,
    max_screenshot_width: int = 1280,
    screenshot_quality: int = 85,
) -> None:
    """
    Connect to ParaView and run the v3 MCP server over streamable-http.

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
    # Construct the ParaView manager with the CLI-provided screenshot settings
    # and install it for the tool function to use.
    set_pv_manager(
        ParaViewManager(
            compress_screenshots=compress_screenshots,
            max_screenshot_width=max_screenshot_width,
            screenshot_quality=screenshot_quality,
        )
    )

    # Connect to ParaView
    pv_manager.connect(paraview_server, paraview_port)

    # Configure the MCP transport bind address before serving.
    mcp.settings.host = mcp_server
    mcp.settings.port = mcp_port

    # Run the MCP server over streamable-http using the configured bind address.
    try:
        logger.info("Starting ParaView External MCP Server (v3)")
        logger.info(f"ParaView server: {paraview_server}:{paraview_port}")
        logger.info(f"MCP server (streamable-http): {mcp_server}:{mcp_port}")
        mcp.run(transport="streamable-http")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error running MCP server: {str(e)}")
