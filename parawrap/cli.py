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
    parser.add_argument(
        "-a", "--auto-prefix",
        action="store_true",
        help="detect a leading '> ' quote or '-'/'1.' list marker per "
             "paragraph and reapply it instead of rewrapping it as text",
    )
    parser.add_argument(
        "-y", "--hyphenate",
        action="store_true",
        help="break words wider than the target width across lines with "
             "a '-', instead of letting them overflow (URLs and email "
             "addresses are still kept intact)",
    )
    parser.add_argument(
        "-j", "--justify",
        action="store_true",
        help="pad inter-word spacing so every line except a paragraph's "
             "last reaches exactly the target width",
    )
    parser.add_argument(
        "--print-completion",
        choices=("bash", "zsh"),
        help="print a shell completion script for the given shell and exit",
    )
    return parser


def _bash_completion_script(parser):
    """Build a bash completion script listing every flag from parser.

    Options are read off the parser rather than hardcoded so the script
    can't silently drift out of sync with build_parser().
    """
    opts = [opt for action in parser._actions for opt in action.option_strings]
    return """\
_parawrap_complete()
{{
    local cur opts
    COMPREPLY=()
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    opts="{opts}"
    if [[ "$cur" == -* ]]; then
        COMPREPLY=( $(compgen -W "$opts" -- "$cur") )
        return 0
    fi
    COMPREPLY=( $(compgen -f -- "$cur") )
}}
complete -F _parawrap_complete parawrap
""".format(opts=" ".join(opts))


def _zsh_completion_script(parser):
    """Build a zsh completion script (an _arguments spec) from parser."""
    specs = []
    for action in parser._actions:
        if not action.option_strings:
            continue
        help_text = (action.help or "").replace("'", "'\\''")
        help_text = help_text.replace("[", "\\[").replace("]", "\\]")
        names = action.option_strings
        if len(names) > 1:
            head = "(" + " ".join(names) + ")" + "{" + ",".join(names) + "}"
        else:
            head = names[0]
        takes_value = action.nargs != 0
        tail = "[{}]".format(help_text) + (":value:" if takes_value else "")
        specs.append("'{}{}'".format(head, tail))
    specs.append("'*:file:_files'")
    body = " \\\n  ".join(specs)
    return "#compdef parawrap\n_arguments \\\n  {}\n".format(body)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.print_completion:
        if args.print_completion == "bash":
            print(_bash_completion_script(parser), end="")
        else:
            print(_zsh_completion_script(parser), end="")
        return 0

    if args.file:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    try:
        result = wrap_text(
            text,
            width=args.width,
            prefix=args.prefix,
            auto_prefix=args.auto_prefix,
            hyphenate=args.hyphenate,
            justify=args.justify,
        )
    except ValueError as exc:
        parser.error(str(exc))
        return 2

    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
