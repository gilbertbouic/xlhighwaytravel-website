#!/usr/bin/env python3
"""Restore the Guided tours section tag dropped during the MSC insert."""
from pathlib import Path

SPECIALS = Path(__file__).resolve().parents[1] / "specials.html"


def main() -> None:
    text = SPECIALS.read_text(encoding="utf-8")
    text = text.replace("\x02", "")
    if 'id="tours"' in text:
        SPECIALS.write_text(text, encoding="utf-8")
        print("tours wrapper already present")
        return
    needle = (
        '</section>\n'
        '<div class="special-section-head reveal">\n'
        '<div class="special-section-copy">\n'
        '<span class="section-kicker">Save up to 30%'
    )
    insert = (
        '</section>\n'
        '<section class="special-section" id="tours">\n'
        '<div class="special-section-head reveal">\n'
        '<div class="special-section-copy">\n'
        '<span class="section-kicker">Save up to 30%'
    )
    if needle not in text:
        raise SystemExit("tours head not found")
    text = text.replace(needle, insert, 1)
    if 'id="tours"' not in text:
        raise SystemExit("tours id still missing")
    SPECIALS.write_text(text, encoding="utf-8")
    print("restored tours section")


if __name__ == "__main__":
    main()
