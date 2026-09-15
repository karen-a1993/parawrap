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

ANSI color/style escape codes (e.g. from `grep --color` or a syntax
highlighter) are measured as zero width, so colored text wraps the same
as its plain equivalent instead of running short to make room for
invisible bytes.

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

By default a word wider than the target width (a URL, a long path) is
placed alone on its own line rather than being split apart. Pass
`-y`/`--hyphenate` to break such words across lines instead, with a
trailing `-` at each break:

    $ parawrap -y -w 10 <<< "supercalifragilisticexpialidocious"
    supercali-
    fragilist-
    icexpiali-
    docious

This is a width-driven cut, not real dictionary hyphenation, so breaks
don't respect syllable boundaries. URLs and email addresses (anything
containing `/` or `@`) are still kept intact even with `-y`, since a
broken URL is useless regardless of how it looks.

Pass `-j`/`--justify` to pad inter-word spacing so both margins line up,
the way `fmt -s` or a typeset paragraph would. A paragraph's last line is
left ragged, and a line with only one word can't be stretched:

    $ parawrap -j -w 20 <<< "the quick brown fox jumps over the lazy dog"
    the  quick brown fox
    jumps  over the lazy
    dog

## Shell completion

Print a completion script for bash or zsh with `--print-completion`:

    $ parawrap --print-completion bash >> ~/.bashrc
    $ parawrap --print-completion zsh > "${fpath[1]}/_parawrap"

The script is generated from the same argument parser the CLI uses, so it
stays in sync with the actual flags instead of being a second copy of
them to maintain by hand.

## Install

No dependencies beyond the standard library.

    $ pip install -e .

## Status

Early. The wrapping core and CLI work; see the test suite in `tests/`
for the cases it's expected to handle correctly.

## License

MIT, see LICENSE.
