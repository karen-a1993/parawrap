import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from parawrap import __version__
from parawrap.cli import build_parser, main, _bash_completion_script, _zsh_completion_script


ALL_OPTS = (
    "-w", "--width", "-p", "--prefix", "-a", "--auto-prefix",
    "-y", "--hyphenate", "-j", "--justify",
)


class CompletionScriptTests(unittest.TestCase):
    def test_bash_script_lists_all_options(self):
        script = _bash_completion_script(build_parser())
        for opt in ALL_OPTS:
            self.assertIn(opt, script)
        self.assertIn("complete -F _parawrap_complete parawrap", script)

    def test_zsh_script_lists_all_options(self):
        script = _zsh_completion_script(build_parser())
        self.assertTrue(script.startswith("#compdef parawrap"))
        for opt in ALL_OPTS:
            self.assertIn(opt, script)
        self.assertIn("_files", script)

    def test_zsh_script_marks_value_taking_options(self):
        # -w/--width takes an argument, so its spec should offer a value
        # placeholder; a flag like -a/--auto-prefix should not.
        script = _zsh_completion_script(build_parser())
        self.assertIn("--width}[", script)
        width_spec = next(line for line in script.splitlines() if "--width}" in line)
        self.assertIn(":value:", width_spec)
        auto_prefix_spec = next(
            line for line in script.splitlines() if "--auto-prefix}" in line
        )
        self.assertNotIn(":value:", auto_prefix_spec)

    def test_main_prints_bash_completion_and_does_not_read_stdin(self):
        out = io.StringIO()
        with redirect_stdout(out):
            status = main(["--print-completion", "bash"])
        self.assertEqual(status, 0)
        self.assertIn("_parawrap_complete", out.getvalue())

    def test_main_prints_zsh_completion_and_does_not_read_stdin(self):
        out = io.StringIO()
        with redirect_stdout(out):
            status = main(["--print-completion", "zsh"])
        self.assertEqual(status, 0)
        self.assertIn("#compdef parawrap", out.getvalue())


class VersionAndFileErrorTests(unittest.TestCase):
    def test_version_flag_prints_package_version(self):
        out = io.StringIO()
        with redirect_stdout(out), self.assertRaises(SystemExit) as ctx:
            main(["--version"])
        self.assertEqual(ctx.exception.code, 0)
        self.assertEqual(out.getvalue().strip(), "parawrap " + __version__)

    def test_missing_file_exits_with_usage_error(self):
        err = io.StringIO()
        with redirect_stderr(err), self.assertRaises(SystemExit) as ctx:
            main(["/nonexistent/parawrap-no-such-file.txt"])
        self.assertEqual(ctx.exception.code, 2)
        self.assertIn("cannot read", err.getvalue())

    def test_non_utf8_file_exits_with_usage_error(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "latin1.txt")
            with open(path, "wb") as f:
                f.write(b"caf\xe9 au lait")
            err = io.StringIO()
            with redirect_stderr(err), self.assertRaises(SystemExit) as ctx:
                main([path])
        self.assertEqual(ctx.exception.code, 2)
        self.assertIn("not valid UTF-8", err.getvalue())


if __name__ == "__main__":
    unittest.main()
