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


def main() -> None:
    """Parse arguments, configure logging, and run the ParaView MCP server."""
    args = parse_args()
    logger = setup_logging()

    # Make an external ParaView install importable before importing the
    # engine module (which imports paraview.simple at import time).
    if args.paraview_package_path:
        sys.path.append(args.paraview_package_path)

    try:
        if args.engine == "v1":
            # Imported lazily, after sys.path is extended, because importing
            # this module pulls in paraview.simple.
            from paraview_mcp.v1 import pv_mcp

            pv_mcp.run(
                server=args.paraview_server,
                port=args.paraview_port,
                compress_screenshots=args.compress_screenshots,
                max_screenshot_width=args.max_screenshot_width,
                screenshot_quality=args.screenshot_quality,
            )
        elif args.engine == "v2":
            # Imported lazily, after sys.path is extended, because importing
            # this module pulls in paraview.simple.
            from paraview_mcp.v2 import pv_mcp

            pv_mcp.run(
                paraview_server=args.paraview_server,
                paraview_port=args.paraview_port,
                mcp_server=args.server,
                mcp_port=args.port,
                compress_screenshots=args.compress_screenshots,
                max_screenshot_width=args.max_screenshot_width,
                screenshot_quality=args.screenshot_quality,
            )
        else:
            raise NotImplementedError(
                f"The '{args.engine}' engine is not implemented yet."
            )
    except Exception as e:  # pragma: no cover - top-level safety net
        logger.error(f"Fatal error starting ParaView MCP server: {str(e)}")
        raise


if __name__ == "__main__":
    main()
