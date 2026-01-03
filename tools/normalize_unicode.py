#!/usr/bin/env python3
"""Report and normalize hidden Unicode characters in tracked text files."""
from __future__ import annotations

import argparse
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

_BOM_BYTES = b"\xef\xbb\xbf"
_BANNED_SEQUENCES = {
    codepoint: chr(codepoint).encode("utf-8") for codepoint in BANNED_CODEPOINTS
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


def _scan_bytes(data: bytes) -> tuple[bool, set[int]]:
    has_bom = data.startswith(_BOM_BYTES)
    found = {
        codepoint
        for codepoint, sequence in _BANNED_SEQUENCES.items()
        if sequence in data
    }
    return has_bom, found


def _normalize_bytes(data: bytes) -> bytes:
    if data.startswith(_BOM_BYTES):
        data = data[len(_BOM_BYTES) :]
    for sequence in _BANNED_SEQUENCES.values():
        data = data.replace(sequence, b"")
    data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return data


def _report_file(path: Path) -> tuple[bool, str]:
    data = path.read_bytes()
    has_bom, found = _scan_bytes(data)
    if not has_bom and not found:
        return False, ""
    details = []
    if has_bom:
        details.append("BOM")
    if found:
        details.append(
            "codepoints="
            + ",".join(f"U+{codepoint:04X}" for codepoint in sorted(found))
        )
    return True, f"{path}: " + "; ".join(details)


def _write_file(path: Path) -> bool:
    original = path.read_bytes()
    normalized = _normalize_bytes(original)
    if normalized != original:
        path.write_bytes(normalized)
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="rewrite files in place")
    args = parser.parse_args()

    issues = []
    changed = []
    for path in _iter_tracked_files():
        has_issue, detail = _report_file(path)
        if has_issue:
            issues.append(detail)
        if args.write and _write_file(path):
            changed.append(str(path))

    if args.write and changed:
        print("Normalized files:")
        for item in changed:
            print(f"- {item}")

    if issues:
        print("Hidden Unicode report:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("No hidden Unicode detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
