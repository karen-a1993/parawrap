# parawrap

`fold` and `fmt` are usually right there, but they measure width in bytes
or codepoints, not what a terminal actually renders. That falls apart on
CJK text, where each character prints two columns wide but counts as one
codepoint, and on plain `textwrap`, which will split a long URL in half
to hit the target width.

parawrap is a small command line tool that reflows plain text to a fixed
column width using terminal display width, and never breaks a word in
the middle.

## Usage

    $ echo "the quick brown fox jumps over the lazy dog" | parawrap -w 20
    the quick brown fox
    jumps over the lazy
    dog

Read from a file instead of stdin:

    $ parawrap -w 72 notes.txt

Prefix every output line, e.g. for quoting in an email reply:

    $ parawrap -w 68 -p "> " reply.txt
    > the quick brown fox jumps over the lazy dog and then a
    > bit more text that needed a second line

Blank lines are treated as paragraph breaks and preserved; everything
else (existing line breaks, tabs, runs of spaces) is collapsed before
the text is rewrapped, so re-running parawrap on already-wrapped text
reflows it cleanly instead of stacking indents.

A word wider than the target width (a URL, a long path) is placed alone
on its own line rather than being split apart.

Auto-detect a quote or list marker at the start of a paragraph and
reapply it instead of rewrapping it as text, with `-a`:

    $ parawrap -a -w 20 <<< "> the quick brown fox jumps over the lazy dog"
    > the quick brown
    > fox jumps over the
    > lazy dog

    $ parawrap -a -w 20 <<< "- the quick brown fox jumps over the lazy dog"
    - the quick brown
      fox jumps over the
      lazy dog

Quote markers (`>`, `>>`, ...) repeat on every wrapped line. List markers
(`-`, `*`, `+`, `1.`, `2)`) appear once, and continuation lines get a
blank hanging indent of the same width instead. `-a` can be combined
with `-p` to add a prefix on top of a detected marker. A paragraph with
more than one bulleted line and no blank line between items is left
untouched, since there is no reliable way to tell where one item ends
and the next begins.

## Install

No dependencies beyond the standard library.

    $ pip install -e .

## Status

Early. The wrapping core and CLI work; see the test suite in `tests/`
for the cases it's expected to handle correctly.

## License

MIT, see LICENSE.
