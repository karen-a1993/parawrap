import unittest

from parawrap.wrap import wrap_text, display_width


# (case name, input text, width, prefix, expected output)
WRAP_CASES = [
    ("empty string", "", 70, "", ""),
    (
        "basic reflow",
        "the quick brown fox jumps over the lazy dog",
        20,
        "",
        "the quick brown fox\njumps over the lazy\ndog",
    ),
    (
        "single word longer than width is not broken",
        "https://example.com/a/very/long/path/that/does/not/fit",
        20,
        "",
        "https://example.com/a/very/long/path/that/does/not/fit",
    ),
    (
        "internal newlines and extra whitespace collapse",
        "line one\nline   two\n   line three",
        70,
        "",
        "line one line two line three",
    ),
    (
        "multiple blank lines collapse to one paragraph break",
        "first paragraph\n\n\n\nsecond paragraph",
        70,
        "",
        "first paragraph\n\nsecond paragraph",
    ),
    (
        "tabs expand before measuring width",
        "a\tb\tc",
        70,
        "",
        "a b c",
    ),
    (
        "prefix is applied to every line and narrows available width",
        "one two three four five",
        10,
        "> ",
        "> one two\n> three\n> four\n> five",
    ),
    (
        "word exactly filling the width stays on one line",
        "aaaaaaaaaa",
        10,
        "",
        "aaaaaaaaaa",
    ),
    (
        "trailing and leading whitespace on lines is stripped",
        "  padded line  \n  another  ",
        70,
        "",
        "padded line another",
    ),
]


class WrapTextTableTests(unittest.TestCase):
    def test_cases(self):
        for name, text, width, prefix, expected in WRAP_CASES:
            with self.subTest(name):
                self.assertEqual(wrap_text(text, width=width, prefix=prefix), expected)


# (case name, input text, expected display width)
DISPLAY_WIDTH_CASES = [
    ("ascii", "hello", 5),
    ("empty string", "", 0),
    ("cjk characters count double", "你好", 4),  # "ni hao"
    ("mixed ascii and wide", "a你b", 4),
    ("combining marks add no width", "é", 1),  # e + combining acute accent
]


class DisplayWidthTableTests(unittest.TestCase):
    def test_cases(self):
        for name, text, expected in DISPLAY_WIDTH_CASES:
            with self.subTest(name):
                self.assertEqual(display_width(text), expected)


if __name__ == "__main__":
    unittest.main()
