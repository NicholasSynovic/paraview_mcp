"""
Command-line interface for the ParaView MCP server.

Thin argparse wrapper that defines the CLI surface and returns the parsed
arguments. Importing this module does not require ParaView; the actual
server is imported and run by ``paraview_mcp.main``.
"""

import argparse


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """
    Parse command-line arguments for the ParaView MCP server.

    Args:
        argv: Optional list of arguments to parse. Defaults to ``sys.argv``.

    Returns:
        The parsed argument namespace with ``server``, ``port`` and
        ``paraview_package_path`` attributes.
    """
    parser = argparse.ArgumentParser(description="ParaView External MCP Server")
    parser.add_argument(
        "--server",
        type=str,
        default="localhost",
        help="ParaView server hostname (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=11111,
        help="ParaView server port (default: 11111)",
    )
    parser.add_argument(
        "--paraview_package_path",
        type=str,
        help="Path to the ParaView Python package",
        default=None,
    )

    return parser.parse_args(argv)
