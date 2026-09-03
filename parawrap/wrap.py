"""Core text wrapping logic."""

import re
import unicodedata

# A run of one or more '>' with an optional trailing space, e.g. "> " or
# ">>". Quote markers repeat on every wrapped line, so nested replies
# ("> > text") stay nested.
_QUOTE_RE = re.compile(r"^(>+ ?)")

# A bullet ("-", "*", "+") or a number ("1.", "2)") followed by spaces.
# List markers appear once per item, so wrapped continuation lines get a
# blank hanging indent of the same width instead of repeating the bullet.
_LIST_RE = re.compile(r"^([-*+]|\d{1,9}[.)]) +")


def display_width(text):
    """Return the terminal column width of text.

    len() counts codepoints, not printed columns. East Asian wide and
    fullwidth characters take two columns, and combining marks take
    zero, so plain length is the wrong measure to wrap against.
    """
    width = 0
    for ch in text:
        if unicodedata.combining(ch):
            continue
        if unicodedata.east_asian_width(ch) in ("W", "F"):
            width += 2
        else:
            width += 1
    return width


def _split_paragraphs(text):
    """Split text into paragraphs of raw, tab-expanded lines.

    Blank lines separate paragraphs. Lines are kept as-is (not yet
    whitespace-collapsed) so callers can inspect a paragraph's leading
    markers before that information is thrown away.
    """
    paragraphs = []
    current = []
    for line in text.splitlines():
        expanded = line.expandtabs(8)
        if expanded.strip() == "":
            if current:
                paragraphs.append(current)
                current = []
        else:
            current.append(expanded)
    if current:
        paragraphs.append(current)
    return paragraphs


def _detect_marker(lines):
    """Find a quote or list marker shared by a paragraph's raw lines.

    Returns (marker, hanging_indent):
      - quote markers (">") repeat on every line, so hanging_indent is
        the same string as marker.
      - list markers ("-", "1.") appear once, so hanging_indent is
        blank padding of the same display width, keeping wrapped lines
        aligned under the item text instead of repeating the bullet.

    A list paragraph is only recognized as a single item: if a later
    line also looks like a bullet, this is probably several list items
    without a blank line between them, which collapsing would mangle,
    so detection backs off and returns (None, None).
    """
    visible = [line.lstrip() for line in lines if line.strip()]
    if not visible:
        return None, None

    quote_match = _QUOTE_RE.match(visible[0])
    if quote_match:
        marker = quote_match.group(1)
        if all(line.startswith(marker) for line in visible):
            return marker, marker

    list_match = _LIST_RE.match(visible[0])
    if list_match and not any(_LIST_RE.match(line) for line in visible[1:]):
        marker = list_match.group(0)
        return marker, " " * display_width(marker)

    return None, None


def _strip_marker(line, marker):
    stripped = line.lstrip()
    if stripped.startswith(marker):
        return stripped[len(marker):]
    return stripped


def _prepare_paragraph(lines, auto_prefix):
    """Collapse a paragraph's raw lines and pick its wrap prefixes.

    Returns (text, marker, hanging_indent), where marker/hanging_indent
    are "" when auto_prefix is off or no marker was detected.
    """
    marker = ""
    hanging = ""
    work = lines
    if auto_prefix:
        detected, hang = _detect_marker(lines)
        if detected:
            marker, hanging = detected, hang
            repeats = marker == hanging
            work = []
            marker_stripped = False
            for line in lines:
                if line.strip() and (repeats or not marker_stripped):
                    work.append(_strip_marker(line, marker))
                    marker_stripped = True
                else:
                    work.append(line)
    text = " ".join(line.strip() for line in work if line.strip())
    return text, marker, hanging


def wrap_paragraph(paragraph, width, prefix="", subsequent_prefix=None):
    """Wrap a single paragraph (no embedded blank lines) to width.

    Words are never split, so a word wider than the available width
    is placed alone on its own line and allowed to overflow - that is
    what keeps URLs and other long tokens intact instead of mangling
    them.

    subsequent_prefix, if given, is used for every line after the
    first instead of prefix - this is what lets a list marker like
    "- " appear once while later lines get a blank hanging indent.
    """
    if subsequent_prefix is None:
        subsequent_prefix = prefix
    available = max(width - max(display_width(prefix), display_width(subsequent_prefix)), 1)
    words = paragraph.split()
    if not words:
        return []

    lines = []
    current = []
    current_width = 0
    for word in words:
        word_width = display_width(word)
        added_width = word_width if not current else current_width + 1 + word_width
        if current and added_width > available:
            lines.append((prefix if not lines else subsequent_prefix) + " ".join(current))
            current = [word]
            current_width = word_width
        else:
            current.append(word)
            current_width = added_width
    if current:
        lines.append((prefix if not lines else subsequent_prefix) + " ".join(current))
    return lines


def wrap_text(text, width=70, prefix="", auto_prefix=False):
    """Rewrap text to width, preserving paragraph breaks.

    Blank lines separate paragraphs. All other whitespace (tabs,
    runs of spaces, existing line breaks) is collapsed before
    rewrapping, so already-wrapped input gets reflowed instead of
    doubled up.

    If auto_prefix is set, each paragraph is checked for a leading
    quote marker ("> ") or list marker ("- ", "1. ") and, when found,
    that marker is stripped before reflowing and reapplied to the
    wrapped output on top of prefix, instead of being treated as part
    of the words.
    """
    if width - display_width(prefix) < 1:
        raise ValueError("width too small for prefix")

    blocks = []
    for lines in _split_paragraphs(text):
        para_text, marker, hanging = _prepare_paragraph(lines, auto_prefix)
        full_prefix = prefix + marker
        full_subsequent = prefix + hanging
        fits = (
            width - display_width(full_prefix) >= 1
            and width - display_width(full_subsequent) >= 1
        )
        if not fits:
            full_prefix = full_subsequent = prefix
        blocks.append(wrap_paragraph(para_text, width, full_prefix, full_subsequent))
    return "\n\n".join("\n".join(lines) for lines in blocks)
