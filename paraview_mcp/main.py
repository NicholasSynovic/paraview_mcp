"""
ParaView MCP server entrypoint.

This is the controller invoked by the ``paraview-mcp`` console script
(``paraview_mcp.main:main``). It parses the CLI arguments, configures
logging, optionally extends ``sys.path`` for an external ParaView install,
then hands off to the MCP server defined in ``paraview_mcp.v1.pv_mcp``.

The server module is imported lazily (inside ``main``) because importing it
pulls in ``paraview.simple`` and constructs the ParaView manager, neither of
which is available without a ParaView build.
"""

import sys

from paraview_mcp.cli import parse_args
from paraview_mcp.logger import setup_logging
from paraview_mcp.v1 import pv_mcp


def main() -> None:
    """Parse arguments, configure logging, and run the ParaView MCP server."""
    args = parse_args()
    logger = setup_logging()

    # Make an external ParaView install importable before importing the
    # server module (which imports paraview.simple at import time).
    if args.paraview_package_path:
        sys.path.append(args.paraview_package_path)

    try:
        pv_mcp.run(server=args.server, port=args.port)
    except Exception as e:  # pragma: no cover - top-level safety net
        logger.error(f"Fatal error starting ParaView MCP server: {str(e)}")
        raise


if __name__ == "__main__":
    main()
