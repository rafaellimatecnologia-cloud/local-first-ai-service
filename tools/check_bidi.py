from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SUSPICIOUS_CODEPOINTS = {
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
    0x2028,  # LS
    0x2029,  # PS
}

ALLOWED_SUFFIXES = {".py", ".md", ".toml", ".yml", ".yaml", ".txt"}
_BOM_BYTES = b"\xef\xbb\xbf"
_SUSPICIOUS_SEQUENCES = {
    codepoint: chr(codepoint).encode("utf-8") for codepoint in SUSPICIOUS_CODEPOINTS
}


def _iter_tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [
        Path(line)
        for line in result.stdout.splitlines()
        if line.strip() and Path(line).suffix in ALLOWED_SUFFIXES
    ]


def _scan_file(path: Path) -> set[int]:
    data = path.read_bytes()
    found = {
        codepoint
        for codepoint, sequence in _SUSPICIOUS_SEQUENCES.items()
        if sequence in data
    }
    if data.startswith(_BOM_BYTES):
        found.add(0xFEFF)
    return found


def main() -> int:
    files = _iter_tracked_files()
    violations: list[str] = []
    for path in files:
        if not path.is_file():
            continue
        found = _scan_file(path)
        if found:
            codepoints = ", ".join(f"U+{codepoint:04X}" for codepoint in sorted(found))
            violations.append(f"{path} contains {codepoints}")
    if violations:
        print("Suspicious bidi/control characters detected:")
        for violation in violations:
            print(f"- {violation}")
        return 1
    print("No suspicious bidi/control characters detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
