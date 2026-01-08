#!/usr/bin/env python3
"""Remove hidden Unicode characters from text files in the repository."""

from __future__ import annotations

import subprocess
from pathlib import Path

TARGET_SUFFIXES = {".py", ".md", ".toml", ".yml", ".yaml", ".txt"}

BANNED_CODEPOINTS = {
    0x00A0,  # NO-BREAK SPACE
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

_BOM_BYTES = b"\xef\xbb\xbf"
_BANNED_SEQUENCES = {codepoint: chr(codepoint).encode("utf-8") for codepoint in BANNED_CODEPOINTS}


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
    text = "".join(ch for ch in text if ord(ch) not in BANNED_CODEPOINTS)
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _strip_banned_bytes(data: bytes) -> bytes:
    if data.startswith(_BOM_BYTES):
        data = data[len(_BOM_BYTES) :]
    for sequence in _BANNED_SEQUENCES.values():
        data = data.replace(sequence, b"")
    return data


def sanitize_file(path: Path) -> bool:
    original_bytes = _read_bytes(path)
    sanitized_bytes = _strip_banned_bytes(original_bytes)
    sanitized_text = sanitize_text(sanitized_bytes.decode("utf-8", errors="ignore"))
    normalized_bytes = sanitized_text.encode("utf-8")
    if normalized_bytes != original_bytes:
        path.write_bytes(normalized_bytes)
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
