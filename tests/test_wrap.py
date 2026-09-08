import unittest

from parawrap.wrap import wrap_text, display_width, strip_ansi


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


# (case name, input text, width, expected output)
AUTO_PREFIX_CASES = [
    (
        "quote marker repeats on every wrapped line",
        "> the quick brown fox jumps over the lazy dog",
        20,
        "> the quick brown\n> fox jumps over the\n> lazy dog",
    ),
    (
        "already-wrapped quote lines collapse and reflow",
        "> line one\n> line two\n> line three",
        70,
        "> line one line two line three",
    ),
    (
        "bullet marker hangs at its own width",
        "- the quick brown fox jumps over the lazy dog",
        20,
        "- the quick brown\n  fox jumps over the\n  lazy dog",
    ),
    (
        "numbered marker hangs at matching width",
        "10. the quick brown fox jumps over the lazy dog",
        20,
        "10. the quick brown\n    fox jumps over\n    the lazy dog",
    ),
    (
        "text without a marker is untouched",
        "the quick brown fox",
        70,
        "the quick brown fox",
    ),
    (
        "several bullets sharing a paragraph are left alone",
        "- item one\n- item two",
        70,
        "- item one - item two",
    ),
    (
        "marker that cannot fit the width is dropped",
        "> hi",
        1,
        "hi",
    ),
]


class AutoPrefixTableTests(unittest.TestCase):
    def test_cases(self):
        for name, text, width, expected in AUTO_PREFIX_CASES:
            with self.subTest(name):
                self.assertEqual(
                    wrap_text(text, width=width, auto_prefix=True), expected
                )

    def test_default_is_off(self):
        text = "> quoted text"
        # without auto_prefix, "> " is just the first word - it is not
        # stripped or reapplied as a wrap prefix.
        self.assertEqual(wrap_text(text, width=70), "> quoted text")


# (case name, input text, expected display width)
DISPLAY_WIDTH_CASES = [
    ("ascii", "hello", 5),
    ("empty string", "", 0),
    ("cjk characters count double", "你好", 4),  # "ni hao"
    ("mixed ascii and wide", "a你b", 4),
    ("combining marks add no width", "é", 1),  # e + combining acute accent
    ("ansi color codes add no width", "\x1b[31mred\x1b[0m", 3),
    ("ansi reset with no color code", "plain\x1b[0m", 5),
]


class DisplayWidthTableTests(unittest.TestCase):
    def test_cases(self):
        for name, text, expected in DISPLAY_WIDTH_CASES:
            with self.subTest(name):
                self.assertEqual(display_width(text), expected)


# (case name, input text, width, expected output)
HYPHENATE_CASES = [
    (
        "overlong word is broken with a trailing hyphen",
        "supercalifragilisticexpialidocious",
        10,
        "supercali-\nfragilist-\nicexpiali-\ndocious",
    ),
    (
        "trailing piece of a hyphenated word combines with the next word",
        "supercalifragilisticexpialidocious hi",
        10,
        "supercali-\nfragilist-\nicexpiali-\ndocious hi",
    ),
    (
        "urls are never hyphenated even if they overflow",
        "https://example.com/a/very/long/path/that/does/not/fit",
        20,
        "https://example.com/a/very/long/path/that/does/not/fit",
    ),
    (
        "email addresses are never hyphenated",
        "someone@example-mail-host.com",
        10,
        "someone@example-mail-host.com",
    ),
    (
        "word that already fits is left alone",
        "hello world",
        20,
        "hello world",
    ),
]


class HyphenateTableTests(unittest.TestCase):
    def test_cases(self):
        for name, text, width, expected in HYPHENATE_CASES:
            with self.subTest(name):
                self.assertEqual(
                    wrap_text(text, width=width, hyphenate=True), expected
                )

    def test_default_is_off(self):
        text = "supercalifragilisticexpialidocious"
        self.assertEqual(wrap_text(text, width=10), text)


class StripAnsiTests(unittest.TestCase):
    def test_removes_color_codes(self):
        self.assertEqual(strip_ansi("\x1b[31mred\x1b[0m"), "red")

    def test_leaves_plain_text_untouched(self):
        self.assertEqual(strip_ansi("plain text"), "plain text")

    def test_wrapping_ignores_escape_codes_in_width(self):
        # A colored word should wrap exactly like its plain equivalent -
        # the escape codes must not count toward the line width.
        colored = "\x1b[31mhello\x1b[0m \x1b[31mworld\x1b[0m"
        self.assertEqual(
            wrap_text(colored, width=5),
            colored.replace(" ", "\n"),
        )


if __name__ == "__main__":
    unittest.main()
