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


_BOM_BYTES = b"\xef\xbb\xbf"
_BANNED_SEQUENCES = {
    codepoint: chr(codepoint).encode("utf-8") for codepoint in BANNED_CODEPOINTS
}


def _scan_file(path: Path) -> set[int]:
    data = path.read_bytes()
    found: set[int] = set()
    if data.startswith(_BOM_BYTES):
        found.add(0xFEFF)
    for codepoint, sequence in _BANNED_SEQUENCES.items():
        if sequence in data:
            found.add(codepoint)
    return found


def test_no_hidden_unicode_characters() -> None:
    violations: list[str] = []
    for path in _iter_tracked_files():
        found = _scan_file(path)
        if found:
            codepoints = ", ".join(f"U+{codepoint:04X}" for codepoint in sorted(found))
            violations.append(f"{path} contains {codepoints}")
    assert not violations, "\n".join([
        "Hidden or bidirectional Unicode characters detected:",
        *violations,
    ])
