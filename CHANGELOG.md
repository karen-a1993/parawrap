# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project has not yet had a tagged release; everything below is
grouped under Unreleased until the first version goes out.

## [Unreleased]

### Added
- Core `wrap_text` / `wrap_paragraph` engine that reflows text to a target
  column width using terminal display width rather than codepoint count,
  so wide CJK characters and zero-width combining marks are measured
  correctly.
- `-w`/`--width` to set the target column width, reading from a file
  argument or stdin.
- Long unbreakable words (URLs, paths) are kept intact on their own line
  instead of being split to hit the width.
- `-p`/`--prefix` to prepend a string to every output line, for quoting.
- `-a`/`--auto-prefix` to detect a leading `>` quote marker or `-`/`*`/`1.`
  list marker per paragraph and reapply it on wrapped output, with list
  continuation lines getting a blank hanging indent instead of a repeated
  bullet.
- ANSI CSI escape codes (color/style) are stripped before measuring width,
  so colored input wraps the same as its plain equivalent.
- `-y`/`--hyphenate` to break overlong words across lines with a trailing
  `-`, skipping anything that looks like a URL or email address.
- `-j`/`--justify` to pad inter-word spacing so both margins line up,
  leaving a paragraph's last line and single-word lines ragged.
- `--print-completion` to emit a bash or zsh completion script generated
  from the CLI's own argument parser.
- PyPI packaging metadata in `pyproject.toml`, with the version
  single-sourced from `parawrap.__version__`.
