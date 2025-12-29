from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SUSPICIOUS_CODEPOINTS = {
    0x202A,  # LRE
    0x202B,  # RLE
    0x202C,  # PDF
    0x202D,  # LRO
    0x202E,  # RLO
    0x2066,  # LRI
    0x2067,  # RLI
    0x2068,  # FSI
    0x2069,  # PDI
    0x200E,  # LRM
    0x200F,  # RLM
    0x2028,  # LS
    0x2029,  # PS
}


def _iter_tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [Path(line) for line in result.stdout.splitlines() if line.strip()]


def _scan_file(path: Path) -> list[tuple[int, int, int]]:
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = path.read_text(encoding="utf-8", errors="ignore")
    findings: list[tuple[int, int, int]] = []
    for line_idx, line in enumerate(content.splitlines(), start=1):
        for col_idx, ch in enumerate(line, start=1):
            codepoint = ord(ch)
            if codepoint in SUSPICIOUS_CODEPOINTS:
                findings.append((line_idx, col_idx, codepoint))
    return findings


def main() -> int:
    files = _iter_tracked_files()
    violations: list[str] = []
    for path in files:
        if not path.is_file():
            continue
        for line, col, codepoint in _scan_file(path):
            violations.append(
                f"{path}:{line}:{col} contains U+{codepoint:04X}"
            )
    if violations:
        print("Suspicious bidi/control characters detected:")
        for violation in violations:
            print(f"- {violation}")
        return 1
    print("No suspicious bidi/control characters detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
