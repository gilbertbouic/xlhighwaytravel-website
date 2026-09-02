#!/usr/bin/env python3
"""Remove duplicate HQ live cards that repeat handwritten specials."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SPECIALS = ROOT / "specials.html"
PUBLISH = ROOT / "scripts" / "publish_specials.py"


def clear_live_block(text: str) -> str:
    updated, n = re.subn(
        r"<!-- LIVE-SPECIALS:START -->.*?<!-- LIVE-SPECIALS:END -->",
        "<!-- LIVE-SPECIALS:START -->\n<!-- LIVE-SPECIALS:END -->",
        text,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit(f"live markers count {n}")
    return updated


def patch_publish() -> None:
    text = PUBLISH.read_text(encoding="utf-8")
    text = text.replace(
        "FEATURED_IDS = {23472, 23877}",
        "FEATURED_IDS = {23472, 23877, 24316}",
    )
    if "uniworld|" not in text:
        text = text.replace(
            'r"jumeirah|thompsons|virgin atlantic|',
            'r"uniworld|club med|phuket|jumeirah|thompsons|virgin atlantic|',
        )
    if "Uniworld," not in text:
        text = text.replace(
            "Cape Town, Jumeirah, Virgin, NCL, tours, Avis,",
            "Cape Town, Jumeirah, Virgin, NCL, Uniworld, Club Med, tours, Avis,",
        )
        text = text.replace(
            "Cape Town, Jumeirah, Virgin, Hurtigruten, tours, Avis,",
            "Cape Town, Jumeirah, Virgin, NCL, Uniworld, Club Med, tours, Avis,",
        )
    if "def run(" not in text:
        raise SystemExit("publish_specials.py is incomplete")
    PUBLISH.write_text(text, encoding="utf-8")


def main() -> None:
    text = SPECIALS.read_text(encoding="utf-8")
    text = clear_live_block(text)
    if 'id="live-24316"' in text or "More from Uniworld" in text:
        raise SystemExit("duplicate Uniworld cards still present")
    SPECIALS.write_text(text, encoding="utf-8")
    patch_publish()
    print("removed live duplicate specials")


if __name__ == "__main__":
    main()
