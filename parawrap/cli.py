"""Command line entry point for parawrap."""

import argparse
import sys

from .wrap import wrap_text


def build_parser():
    parser = argparse.ArgumentParser(
        prog="parawrap",
        description="Reflow plain text to a fixed line width.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="file to read (default: stdin)",
    )
    parser.add_argument(
        "-w", "--width",
        type=int,
        default=70,
        help="target line width in columns (default: 70)",
    )
    parser.add_argument(
        "-p", "--prefix",
        default="",
        help="string to prepend to every output line, e.g. '> '",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.file:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    try:
        result = wrap_text(text, width=args.width, prefix=args.prefix)
    except ValueError as exc:
        parser.error(str(exc))
        return 2

    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
