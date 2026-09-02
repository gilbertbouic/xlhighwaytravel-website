#!/usr/bin/env python3
"""Add current HQ specials to specials.html as deal cards.

Fetches TravelFind categories 158 and 159. Skips campaigns already written
up on the page (Cape Town, Jumeirah, Virgin, NCL, tours, Avis,
Castleburn, One&Only, DSC Transfers, Bakubung / Kwa Maritane). Airlink is not from HQ and is left untouched.

Usage:
  python3 scripts/publish_specials.py
  python3 scripts/publish_specials.py --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import time
import urllib.request
from datetime import datetime, timezone
from html import escape, unescape
from io import BytesIO
from pathlib import Path
from urllib.parse import quote, urlparse

try:
    from PIL import Image
except ImportError as e:  # pragma: no cover
    raise SystemExit("Pillow is required: pip install Pillow") from e

SITE_ROOT = Path(__file__).resolve().parents[1]
SPECIALS_HTML = SITE_ROOT / "specials.html"
IMG_ROOT = SITE_ROOT / "assets" / "img" / "specials" / "live"
MARKER_START = "<!-- LIVE-SPECIALS:START -->"
MARKER_END = "<!-- LIVE-SPECIALS:END -->"

CATEGORY_URL = "https://xl-api-s.travelfind.me/api/content/category"
CATEGORIES = ((158, "Campaigns"), (159, "Travel Tip Tuesday"))
USER_AGENT = "XLHighwayTravel-SpecialsSync/1.0 (+https://xlhighwaytravel.co.za)"
UPLOAD_READ = "https://xl-api-s.travelfind.me/api/upload/read/"

# Already presented as hand-written sections — do not emit a second copy.
FEATURED_IDS = {23472, 23877}
FEATURED_NAME_RE = re.compile(
    r"jumeirah|thompsons|virgin atlantic|hurtigruten|norwegian cruise|\bncl\b|development promotions|"
    r"\bavis\b|castleburn|legacy hotels|portswood|commodore|"
    r"bakubung|bakubang|kwa.?maritane|pilanesberg|one.?only|dsc transfers|"
    r"\bttc\b|trafalg|costsaver|insight vacation|madagascar|\bmsc\b",
    re.I,
)

MAX_IMAGE_WIDTH = 1400
WEBP_QUALITY = 82
MAX_CARDS = 4
PRICE_RE = re.compile(r"R\s*([0-9]{1,3}(?:[\s,][0-9]{3})+|[0-9]{3,})")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    s = value.strip()
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def http_get_json(url: str) -> object:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


def http_get_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def parse_files(field: object) -> list[dict]:
    if not field:
        return []
    if isinstance(field, list):
        return [f for f in field if isinstance(f, dict)]
    if isinstance(field, str):
        try:
            data = json.loads(field)
        except json.JSONDecodeError:
            return []
        if isinstance(data, list):
            return [f for f in data if isinstance(f, dict)]
    return []


def file_url(entry: dict) -> str | None:
    for key in ("fileUrl", "url", "path", "src", "href"):
        v = entry.get(key)
        if isinstance(v, str) and v.startswith("http"):
            return v
    for key in ("fileName", "hash", "guid"):
        v = entry.get(key)
        if isinstance(v, str) and re.fullmatch(r"[a-fA-F0-9]{16,}", v):
            return f"{UPLOAD_READ}{v}"
    return None


def promotion_assets(item: dict) -> list[dict]:
    out = []
    for entry in parse_files(item.get("fileName")):
        label = (entry.get("fileLabel") or entry.get("label") or "").strip().lower()
        if label != "promotion":
            continue
        url = file_url(entry)
        if not url:
            continue
        host = (urlparse(url).hostname or "").lower()
        if host.endswith("xltravel.co.za"):
            continue
        out.append({"url": url, "name": entry.get("name") or ""})
    return out


def clean_title(name: str) -> str:
    n = name or "Travel special"
    n = re.sub(r"^\s*XL\s*\|\s*", "", n, flags=re.I)
    n = re.sub(r"^\s*Travel Tip Tuesday\b[\s\-–—:]*", "", n, flags=re.I)
    n = re.sub(r"^\(\d{1,2}/\d{1,2}/\d{4}\)\s*[-–—:]?\s*", "", n)
    n = re.sub(
        r"\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
        "",
        n,
        flags=re.I,
    )
    n = re.sub(r"\s+Campaign\s*$", "", n, flags=re.I)
    n = re.sub(
        r"\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s*$",
        "",
        n,
        flags=re.I,
    )
    n = re.sub(r"\s+", " ", n).strip(" -–—")
    return n or "Travel special"


def is_duplicate(item: dict, title: str) -> bool:
    if item.get("id") in FEATURED_IDS:
        return True
    blob = f"{item.get('name') or ''} {title}"
    return bool(FEATURED_NAME_RE.search(blob))


def is_public(item: dict, now: datetime) -> bool:
    if not isinstance(item, dict) or item.get("isDeleted"):
        return False
    if not promotion_assets(item):
        return False
    end = parse_dt(item.get("specialsEnd"))
    if end and end <= now:
        return False
    if not end and item.get("isActive") is False:
        return False
    return True


def parse_rand_amounts(text: str) -> list[int]:
    amounts = []
    for match in PRICE_RE.finditer(text or ""):
        digits = re.sub(r"\D", "", match.group(1))
        if not digits:
            continue
        value = int(digits)
        if 200 <= value <= 500000:
            amounts.append(value)
    return amounts


def format_rand(value: int) -> str:
    return "R" + f"{value:,}".replace(",", " ")


def extract_from_price(texts: list[str]) -> tuple[int | None, str | None]:
    amounts: list[int] = []
    for text in texts:
        amounts.extend(parse_rand_amounts(text))
    if not amounts:
        return None, None
    lowest = min(amounts)
    return lowest, format_rand(lowest)


def ocr_image(path: Path) -> str:
    try:
        import pytesseract
    except ImportError:
        return ""
    try:
        with Image.open(path) as im:
            return pytesseract.image_to_string(im) or ""
    except Exception:
        return ""


def to_webp(raw: bytes, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(BytesIO(raw)) as im:
        if im.mode != "RGB":
            im = im.convert("RGB")
        if im.width > MAX_IMAGE_WIDTH:
            ratio = MAX_IMAGE_WIDTH / float(im.width)
            im = im.resize((MAX_IMAGE_WIDTH, max(1, int(im.height * ratio))), Image.Resampling.LANCZOS)
        tmp = dest.with_suffix(".part.webp")
        im.save(tmp, "WEBP", quality=WEBP_QUALITY, method=6)
        tmp.replace(dest)


def source_key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def publish_images(campaign_id: object, assets: list[dict], skip_download: bool) -> list[str]:
    folder = IMG_ROOT / str(campaign_id)
    folder.mkdir(parents=True, exist_ok=True)
    manifest_path = folder / "manifest.json"
    prev = {}
    if manifest_path.is_file():
        try:
            prev = {
                row["key"]: row
                for row in json.loads(manifest_path.read_text(encoding="utf-8")).get("images") or []
                if isinstance(row, dict) and row.get("key")
            }
        except json.JSONDecodeError:
            prev = {}
    written = []
    rels = []
    for i, asset in enumerate(assets, start=1):
        url = asset["url"]
        key = source_key(url)
        filename = f"{i:02d}.webp"
        dest = folder / filename
        cached = prev.get(key)
        reuse = bool(cached and cached.get("file") == filename and dest.is_file() and dest.stat().st_size > 0)
        if not reuse and not skip_download:
            to_webp(http_get_bytes(url), dest)
            time.sleep(0.12)
        elif not dest.is_file():
            raise FileNotFoundError(f"Missing {dest} and download skipped")
        written.append({"key": key, "file": filename})
        rels.append(f"assets/img/specials/live/{campaign_id}/{filename}")
    keep = {row["file"] for row in written}
    for leftover in folder.glob("*"):
        if leftover.name != "manifest.json" and leftover.name not in keep:
            leftover.unlink()
    manifest_path.write_text(json.dumps({"images": written}, indent=2) + "\n", encoding="utf-8")
    return rels


def assert_no_hq_leak(payload: str, where: str) -> None:
    low = payload.lower()
    if "xltravel.co.za" in low:
        raise SystemExit(f"Refusing to publish: {where} still contains xltravel.co.za")
    if "travelfind.me" in low:
        raise SystemExit(f"Refusing to publish: {where} still contains a TravelFind URL")


def render_section(card: dict) -> str:
    cid = card["id"]
    title = card["title"]
    ends_label = card.get("ends_label")
    images = card["images"][:MAX_CARDS]
    price_label = card.get("price_label")
    interest = quote(title)
    kicker = f"Valid until {ends_label}" if ends_label else "Current offer"
    lead = "Book this offer through XL Highway Travel."
    if price_label:
        lead = f"From {price_label}. " + lead
    if ends_label:
        lead += f" Valid until {ends_label}."

    cards = []
    for i, src in enumerate(images):
        alt = escape(title if i == 0 else f"{title} — {i + 1}")
        price_html = ""
        if i == 0 and price_label:
            price_html = (
                f'<div class="deal-price"><span class="now">{escape(price_label)}</span>'
                f'<span class="unit">from</span></div>'
            )
            save = f'<span class="deal-save">From {escape(price_label)}</span>'
        else:
            save = ""
        heading = escape(title) if i == 0 else escape(f"More from {title}")
        cards.append(
            "<article class=\"deal-card reveal\">\n"
            "<div class=\"deal-card-media\">\n"
            f'<img src="{escape(src)}" alt="{alt}" width="1080" height="1080" loading="lazy">\n'
            f"{save}\n"
            "</div>\n"
            "<div class=\"deal-card-body\">\n"
            f"<span class=\"brand\">{escape(kicker)}</span>\n"
            f"<h3>{heading}</h3>\n"
            f'<p class="meta">{escape(lead) if i == 0 else "Ask us to quote this offer for your dates."}</p>\n'
            f"{price_html}\n"
            f'<a class="btn btn-secondary" href="contact.html?interest={interest}">Enquire</a>\n'
            "</div>\n"
            "</article>"
        )

    return (
        f'<section class="special-section" id="live-{cid}">\n'
        '<div class="special-section-head reveal">\n'
        '<div class="special-section-copy">\n'
        f'<span class="section-kicker">{escape(kicker)}</span>\n'
        f"<h2>{escape(title)}</h2>\n"
        f"<p>{escape(lead)}</p>\n"
        "</div>\n"
        '<div class="special-section-media">\n'
        f'<img src="{escape(images[0])}" alt="{escape(title)}" width="1080" height="1080" loading="lazy">\n'
        "</div>\n"
        "</div>\n"
        f'<div class="deal-grid">\n{chr(10).join(cards)}\n</div>\n'
        "</section>\n"
    )


def inject_html(fragment: str) -> None:
    page = SPECIALS_HTML.read_text(encoding="utf-8")
    if MARKER_START not in page or MARKER_END not in page:
        raise SystemExit("specials.html is missing LIVE-SPECIALS markers")
    block = f"{MARKER_START}\n{fragment}{MARKER_END}"
    new_page = re.sub(
        re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END),
        lambda _: block,
        page,
        count=1,
        flags=re.S,
    )
    assert_no_hq_leak(new_page, "specials.html")
    SPECIALS_HTML.write_text(new_page, encoding="utf-8")


def update_sitemap(today: str) -> None:
    sitemap = SITE_ROOT / "sitemap.xml"
    if not sitemap.is_file():
        return
    text = sitemap.read_text(encoding="utf-8")
    updated, n = re.subn(
        r"(<loc>https://xlhighwaytravel\.co\.za/specials\.html</loc>\s*)<lastmod>[^<]*</lastmod>",
        rf"\1<lastmod>{today}</lastmod>",
        text,
        count=1,
    )
    if n == 0:
        updated = text.replace(
            "<loc>https://xlhighwaytravel.co.za/specials.html</loc>",
            f"<loc>https://xlhighwaytravel.co.za/specials.html</loc>\n    <lastmod>{today}</lastmod>",
            1,
        )
    sitemap.write_text(updated, encoding="utf-8")


def run(dry_run: bool = False, skip_download: bool = False) -> dict:
    now = utc_now()
    chosen: list[dict] = []
    skipped = 0
    for cid, label in CATEGORIES:
        print(f"Fetching {label} ({cid}) …")
        data = http_get_json(f"{CATEGORY_URL}/{cid}")
        items = data if isinstance(data, list) else (data.get("content") or data.get("data") or [])
        for it in items:
            if not is_public(it, now):
                continue
            title = clean_title(it.get("name") or "")
            if is_duplicate(it, title):
                skipped += 1
                print(f"  skip duplicate {it.get('id')} {title}")
                continue
            chosen.append(it)
        print(f"  {len(items)} raw")

    chosen.sort(key=lambda it: parse_dt(it.get("specialsEnd")) or datetime.max.replace(tzinfo=timezone.utc))
    print(f"{len(chosen)} new sections, {skipped} already on the page")
    if dry_run:
        for it in chosen:
            print(f"  + {it.get('id')} {clean_title(it.get('name') or '')}")
        return {"count": len(chosen), "dry_run": True}

    IMG_ROOT.mkdir(parents=True, exist_ok=True)
    cards = []
    for it in chosen:
        title = clean_title(it.get("name") or f"Campaign {it.get('id')}")
        print(f"  publishing {it.get('id')} {title}")
        end = parse_dt(it.get("specialsEnd"))
        images = publish_images(it["id"], promotion_assets(it), skip_download)
        ocr_bits = [ocr_image(SITE_ROOT / rel) for rel in images[:3]]
        desc = unescape(re.sub(r"<[^>]+>", " ", it.get("description") or ""))
        amount, price_label = extract_from_price([desc, *ocr_bits])
        cards.append(
            {
                "id": it.get("id"),
                "title": title,
                "ends_label": end.strftime("%d %b %Y") if end else None,
                "images": images,
                "price_label": price_label,
                "price_amount": amount,
            }
        )

    fragment = "".join(render_section(c) for c in cards)
    inject_html(fragment)

    keep = {str(c["id"]) for c in cards}
    if IMG_ROOT.is_dir():
        for child in IMG_ROOT.iterdir():
            if child.is_dir() and child.name not in keep:
                shutil.rmtree(child)
                print(f"  removed expired {child.name}")

    update_sitemap(now.strftime("%Y-%m-%d"))
    print(f"Updated {SPECIALS_HTML} with {len(cards)} live sections")
    return {"count": len(cards)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sync HQ specials onto specials.html")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-download", action="store_true")
    args = parser.parse_args(argv)
    run(dry_run=args.dry_run, skip_download=args.skip_download)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
