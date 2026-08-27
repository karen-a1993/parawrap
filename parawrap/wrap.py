"""Core text wrapping logic."""

import unicodedata


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
    """Split text into paragraphs on blank lines.

    Each paragraph is returned as a single string with internal
    whitespace already collapsed to single spaces, so callers can
    rewrap it directly.
    """
    paragraphs = []
    current = []
    for line in text.splitlines():
        if line.strip() == "":
            if current:
                paragraphs.append(" ".join(current))
                current = []
        else:
            current.append(line.expandtabs(8).strip())
    if current:
        paragraphs.append(" ".join(current))
    return paragraphs


def wrap_paragraph(paragraph, width, prefix=""):
    """Wrap a single paragraph (no embedded blank lines) to width.

    Words are never split, so a word wider than the available width
    is placed alone on its own line and allowed to overflow - that is
    what keeps URLs and other long tokens intact instead of mangling
    them.
    """
    available = max(width - display_width(prefix), 1)
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
            lines.append(prefix + " ".join(current))
            current = [word]
            current_width = word_width
        else:
            current.append(word)
            current_width = added_width
    if current:
        lines.append(prefix + " ".join(current))
    return lines


def wrap_text(text, width=70, prefix=""):
    """Rewrap text to width, preserving paragraph breaks.

    Blank lines separate paragraphs. All other whitespace (tabs,
    runs of spaces, existing line breaks) is collapsed before
    rewrapping, so already-wrapped input gets reflowed instead of
    doubled up.
    """
    if width - display_width(prefix) < 1:
        raise ValueError("width too small for prefix")

    paragraphs = _split_paragraphs(text)
    blocks = [wrap_paragraph(p, width, prefix) for p in paragraphs]
    return "\n\n".join("\n".join(lines) for lines in blocks)
