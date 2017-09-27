from argparse import ArgumentParser
from collections import OrderedDict

from docker_tools.verify import Verify


def main():
    parser = ArgumentParser()

    subcommands = OrderedDict([
        ("verify", Verify)
    ])

    subparsers = parser.add_subparsers(dest="command")

    for name, cmd in subcommands.items():
        sp = subparsers.add_parser(name, help=cmd.help())
        cmd.addArguments(sp)

    opts = parser.parse_args()

    if not opts.command:
        parser.print_usage()
        return

    subcommands[opts.command]().run(opts)


if __name__ == '__main__':
    main()
