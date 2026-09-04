#!/usr/bin/env python3
"""Restore the Guided tours section tag dropped during the MSC insert."""
from pathlib import Path
import re

SPECIALS = Path(__file__).resolve().parents[1] / "specials.html"


def main() -> None:
    text = SPECIALS.read_text(encoding="utf-8")
    text = text.replace("\x02", "")
    if 'id="tours"' in text:
        SPECIALS.write_text(text, encoding="utf-8")
        print("tours wrapper already present")
        return
    text, n = re.subn(
        r'(</section>\s*)(<div class="special-section-head reveal">\s*<div class="special-section-copy">\s*<span class="section-kicker">Save up to 30%)',
        r'\1<section class="special-section" id="tours">\n\2',
        text,
        count=1,
    )
    if n != 1 or 'id="tours"' not in text:
        raise SystemExit(f"tours restore failed n={n}")
    SPECIALS.write_text(text, encoding="utf-8")
    print("restored tours section")


if __name__ == "__main__":
    main()
