import io
import unittest
from contextlib import redirect_stdout

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


if __name__ == "__main__":
    unittest.main()
