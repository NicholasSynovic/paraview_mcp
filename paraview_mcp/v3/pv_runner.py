from argparse import ArgumentParser, Namespace

from paraview.simple import *


def cli_parser() -> Namespace:
    parser: ArgumentParser = ArgumentParser(
        prog="ParaView Runner",
        description="Connects to a remote ParaView instance and execute arbitary code",
    )
    parser.add_argument(
        "--pv-host",
        type=str,
        default="localhost",
        help="Remote ParaView hostname",
    )
    parser.add_argument(
        "--pv-port",
        type=int,
        default=11111,
        help="Remote ParaView port number",
    )
    parser.add_argument(
        "--code",
        type=str,
        required=True,
        help="`pvpython` code to execute against the remote",
    )
    return parser.parse_args()


def connect(hostname: str, port: int) -> None:
    """
    Connect to a ParaView remote.

    `hostname` and `port` are applied to both the data server and the render
    server.
    """

    Connect(
        ds_host=hostname,
        ds_port=port,
        rs_host=hostname,
        rs_port=port,
    )


def main() -> None:
    args: Namespace = cli_parser()

    # Connect to ParaView remote
    connect(hostname=args.pv_host, port=args.pv_port)

    # Execute the `pvpython` code
    exec(args.code)
