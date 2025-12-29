from __future__ import annotations

import subprocess
from pathlib import Path

BANNED_CODEPOINTS = {
    0xFEFF,  # BOM
    0x200B,  # ZERO WIDTH SPACE
    0x200C,  # ZERO WIDTH NON-JOINER
    0x200D,  # ZERO WIDTH JOINER
    0x2060,  # WORD JOINER
    0x200E,  # LRM
    0x200F,  # RLM
    0x061C,  # ARABIC LETTER MARK
    0x202A,  # LRE
    0x202B,  # RLE
    0x202C,  # PDF
    0x202D,  # LRO
    0x202E,  # RLO
    0x2066,  # LRI
    0x2067,  # RLI
    0x2068,  # FSI
    0x2069,  # PDI
    0x2028,  # LINE SEPARATOR
    0x2029,  # PARAGRAPH SEPARATOR
}

ALLOWED_SUFFIXES = {".py", ".md", ".toml", ".yml", ".yaml", ".txt"}


def _iter_tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    )
    files: list[Path] = []
    for line in result.stdout.splitlines():
        path = Path(line)
        if path.suffix in ALLOWED_SUFFIXES:
            files.append(path)
    return files


def _scan_file(path: Path) -> list[tuple[int, int, int]]:
    content = path.read_text(encoding="utf-8", errors="ignore")
    findings: list[tuple[int, int, int]] = []
    for line_idx, line in enumerate(content.splitlines(), start=1):
        for col_idx, ch in enumerate(line, start=1):
            codepoint = ord(ch)
            if codepoint in BANNED_CODEPOINTS:
                findings.append((line_idx, col_idx, codepoint))
    return findings


def test_no_hidden_unicode_characters() -> None:
    violations: list[str] = []
    for path in _iter_tracked_files():
        for line, col, codepoint in _scan_file(path):
            violations.append(f"{path}:{line}:{col} contains U+{codepoint:04X}")
    assert not violations, "\n".join([
        "Hidden or bidirectional Unicode characters detected:",
        *violations,
    ])
