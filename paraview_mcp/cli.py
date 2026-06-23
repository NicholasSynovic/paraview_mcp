"""
Command-line interface for the ParaView MCP server.

Thin argparse wrapper that defines the CLI surface and returns the parsed
arguments. Importing this module does not require ParaView; the actual
server is imported and run by ``paraview_mcp.main``.
"""

import argparse

from paraview_mcp import __doi__, __prog__


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """
    Parse command-line arguments for the ParaView MCP server.

    Args:
        argv: Optional list of arguments to parse. Defaults to ``sys.argv``.

    Returns:
        The parsed argument namespace. Depending on the chosen sub-command,
        it will contain 'version' ("v1" or "v2") along with the version-specific
        arguments.
    """
    # 1. Define the shared parent parser for ParaView options
    # We set add_help=False so it doesn't conflict with the subparser help flags
    pv_parent = argparse.ArgumentParser(add_help=False)
    pv_group = pv_parent.add_argument_group("ParaView Server Options")
    pv_group.add_argument(
        "--paraview-server",
        type=str,
        default="localhost",
        help="ParaView server hostname (default: %(default)s)",
    )
    pv_group.add_argument(
        "--paraview-port",
        type=int,
        default=11111,
        help="ParaView server port (default: %(default)s)",
    )

    # 2. Define the main root parser
    parser = argparse.ArgumentParser(
        prog=__prog__,
        description="ParaView External MCP Server",
        epilog=f"DOI: {__doi__}",
    )

    subparsers = parser.add_subparsers(
        dest="version", required=True, help="API version to run"
    )

    # =========================================================================
    # --- V1 Subparser Configuration -----------------------------------------
    # =========================================================================
    # Inherits the ParaView options automatically via the parents parameter
    subparsers.add_parser(
        "v1", parents=[pv_parent], help="Run using V1 engine protocols"
    )

    # =========================================================================
    # --- V2 Subparser Configuration -----------------------------------------
    # =========================================================================
    # Inherits the ParaView options via parents, and adds its own MCP options
    v2_parser = subparsers.add_parser(
        "v2", parents=[pv_parent], help="Run using V2 engine protocols"
    )

    v2_mcp_group = v2_parser.add_argument_group("V2 MCP Server Options")
    v2_mcp_group.add_argument(
        "--server",
        type=str,
        default="localhost",
        help="MCP server hostname (default: %(default)s)",
    )
    v2_mcp_group.add_argument(
        "--port",
        type=int,
        default=8080,
        help="MCP port (default: %(default)s)",
    )

    return parser.parse_args(argv)
