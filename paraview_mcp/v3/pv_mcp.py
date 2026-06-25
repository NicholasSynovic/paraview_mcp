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

import shutil
import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Import the prompt and logger from ParaView-free modules (NOT from
# paraview_mcp.tools, which transitively imports manager.py -> paraview.simple).
# This keeps the v3 engine process import-clean of ParaView; only the
# pv_runner.py subprocess (run via pvpython) needs paraview.simple.
from paraview_mcp.logger import setup_logging
from paraview_mcp.prompts import default_prompt

logger = setup_logging()

# The single FastMCP instance for the v3 engine. Distinct from the shared
# instance in ``paraview_mcp.tools`` used by v1/v2.
mcp = FastMCP("ParaView", instructions=default_prompt)

# Standalone runner script invoked as a subprocess by ``execute_code``. Resolved
# relative to this file so it works regardless of the current working directory.
PV_RUNNER = Path(__file__).parent / "pv_runner.py"

# Maximum time (seconds) to wait for the runner subprocess before giving up.
SUBPROCESS_TIMEOUT = 60


# ============================================================================
# MCP Tool for ParaView (v3)
# ============================================================================


@mcp.tool()
def execute_code(code: str) -> dict:
    """
    Execute a Python code string against the ParaView server.

    The code is run by invoking ``pv_runner.py`` as a subprocess under
    ``pvpython``. The runner connects to the default ParaView server
    (localhost:11111) and executes the supplied code in a full
    ``paraview.simple`` session. Standard output and standard error from the
    subprocess are captured and returned.

    Args:
        code: Python source to run on the ParaView server.

    Returns:
        A dict with keys ``returncode`` (int), ``stdout`` (str) and
        ``stderr`` (str).
    """
    pvpython = shutil.which("pvpython")
    if pvpython is None:
        message = "pvpython not found on PATH"
        logger.error(message)
        return {"returncode": -1, "stdout": "", "stderr": message}

    cmd: list[str] = [pvpython, str(PV_RUNNER), "--code", code]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
        )
        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout or ""
        stderr = e.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors="replace")
        timeout_note = (
            f"Subprocess timed out after {SUBPROCESS_TIMEOUT} seconds."
        )
        logger.error(timeout_note)
        stderr = f"{stderr}\n{timeout_note}" if stderr else timeout_note
        return {"returncode": -1, "stdout": stdout, "stderr": stderr}
    except Exception as e:
        message = f"Error running pv_runner.py: {str(e)}"
        logger.error(message)
        return {"returncode": -1, "stdout": "", "stderr": message}


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
