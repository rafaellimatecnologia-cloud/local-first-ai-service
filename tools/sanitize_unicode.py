#!/usr/bin/env python3
"""Remove hidden Unicode characters from text files in the repository."""
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


def iter_tracked_files() -> list[Path]:
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


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def sanitize_text(text: str) -> str:
    if text.startswith("\ufeff"):
        text = text.lstrip("\ufeff")
    return "".join(ch for ch in text if ord(ch) not in BANNED_CODEPOINTS)


def sanitize_file(path: Path) -> bool:
    original_bytes = _read_bytes(path)
    original_text = original_bytes.decode("utf-8", errors="ignore")
    sanitized = sanitize_text(original_text)
    if original_bytes.startswith(b"\xef\xbb\xbf"):
        original_text = original_text.lstrip("\ufeff")
    if sanitized != original_text:
        path.write_text(sanitized, encoding="utf-8", newline="\n")
        return True
    return False


def main() -> None:
    changed = []
    for path in iter_tracked_files():
        if sanitize_file(path):
            changed.append(str(path))
    if changed:
        print("Sanitized files:")
        for item in changed:
            print(f"- {item}")
    else:
        print("No changes needed.")


if __name__ == "__main__":
    main()
