#!/usr/bin/env python3
"""Report hidden Unicode characters in tracked text files."""
from __future__ import annotations

import subprocess
from pathlib import Path

TARGET_SUFFIXES = {".py", ".md", ".toml", ".yml", ".yaml", ".txt"}

BANNED_CODEPOINTS = {
    0xFEFF,  # BOM
    0x200B,  # ZERO WIDTH SPACE
    0x200C,  # ZERO WIDTH NON-JOINER
    0x200D,  # ZERO WIDTH JOINER
    0x2060,  # WORD JOINER
    0x061C,  # ARABIC LETTER MARK
    0x200E,  # LRM
    0x200F,  # RLM
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


def _iter_tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    )
    paths: list[Path] = []
    for line in result.stdout.splitlines():
        path = Path(line)
        if path.suffix in TARGET_SUFFIXES:
            paths.append(path)
    return paths


def _scan_file(path: Path) -> tuple[bool, set[int]]:
    data = path.read_bytes()
    has_bom = data.startswith(b"\xef\xbb\xbf")
    decoded = data.decode("utf-8", errors="ignore")
    found = {ord(ch) for ch in decoded if ord(ch) in BANNED_CODEPOINTS}
    return has_bom, found


def main() -> int:
    issues = []
    for path in _iter_tracked_files():
        has_bom, found = _scan_file(path)
        if has_bom or found:
            details = []
            if has_bom:
                details.append("BOM")
            if found:
                details.append(
                    "codepoints="
                    + ",".join(f"U+{codepoint:04X}" for codepoint in sorted(found))
                )
            issues.append(f"{path}: " + "; ".join(details))
    if issues:
        print("Hidden Unicode report:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("No hidden Unicode detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
