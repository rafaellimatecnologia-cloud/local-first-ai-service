from __future__ import annotations

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
}

ALLOWED_SUFFIXES = {".py", ".md", ".toml", ".yml", ".yaml"}


def _iter_paths() -> list[Path]:
    root = Path(__file__).resolve().parents[1]
    paths = []
    for path in root.rglob("*"):
        if path.is_dir():
            if path.name in {".git", ".venv", "venv", "dist", "build", "__pycache__"}:
                continue
        if path.is_file() and path.suffix in ALLOWED_SUFFIXES:
            paths.append(path)
    return paths


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


def test_no_bidi_unicode_characters() -> None:
    violations: list[str] = []
    for path in _iter_paths():
        for line, col, codepoint in _scan_file(path):
            violations.append(f"{path}:{line}:{col} contains U+{codepoint:04X}")
    assert not violations, "\n".join(["Suspicious bidi/control characters detected:"] + violations)
