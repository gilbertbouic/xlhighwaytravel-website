#!/usr/bin/env python3
"""Sync HQ promotional flyers onto this GitHub Pages site.

Fetches TravelFind categories 158 (campaigns) and 159 (Travel Tip Tuesday),
hosts images locally, strips HQ/supplier links, writes assets/data/specials.json.

Usage (from the site root or this folder):
  python3 scripts/publish_specials.py
  python3 scripts/publish_specials.py --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import time
import urllib.request
from datetime import datetime, timezone
from html import unescape
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

try:
    from PIL import Image
except ImportError as e:  # pragma: no cover
    raise SystemExit("Pillow is required: pip install Pillow") from e

SITE_ROOT = Path(__file__).resolve().parents[1]
CATEGORY_URL = "https://xl-api-s.travelfind.me/api/content/category"
CATEGORIES = (
    (158, "Campaigns"),
    (159, "Travel Tip Tuesday"),
)
# Already written up as curated sections — do not duplicate in the flyer grid.
FEATURED_IDS = {23472}  # Legacy Cape Town winter
USER_AGENT = "XLHighwayTravel-SpecialsSync/1.0 (+https://xlhighwaytravel.co.za)"
UPLOAD_READ = "https://xl-api-s.travelfind.me/api/upload/read/"
ALLOWED_TAGS = {"p", "br", "strong", "em", "b", "i", "ul", "ol", "li", "span"}
MAX_IMAGE_WIDTH = 1400
WEBP_QUALITY = 82


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
    n = re.sub(r"\s+", " ", n).strip()
    return n or "Travel special"


def slugify(name: str, cid: object) -> str:
    base = re.sub(r"[^a-zA-Z0-9]+", "-", clean_title(name)).strip("-").lower()[:48]
    return f"{cid}-{base or 'campaign'}"


def unwrap_anchors(html: str) -> str:
    return re.sub(r"(?is)<a\b[^>]*>(.*?)</a>", r"\1", html)


def sanitize_description(html: str | None) -> str:
    if not html:
        return ""
    text = re.sub(r"(?is)<script.*?>.*?</script>", "", html)
    text = re.sub(r"(?is)<style.*?>.*?</style>", "", text)
    text = unwrap_anchors(text)
    text = re.sub(r"https?://[^\s<\"']+", "", text)
    text = re.sub(r"(?is)\s+href\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+)", "", text)

    def keep_tag(match: re.Match[str]) -> str:
        name = match.group(1).lower()
        closing = match.group(0).lstrip().startswith("</")
        if name not in ALLOWED_TAGS:
            return ""
        if closing:
            return f"</{name}>"
        if name == "br":
            return "<br>"
        return f"<{name}>"

    text = re.sub(r"</?([a-zA-Z0-9]+)([^>]*)/?>", keep_tag, text)
    text = unescape(text)
    text = re.sub(r"(?is)<p>\s*(?:&nbsp;|\u00a0|\s)*</p>", "", text)
    return text.strip()


def tidy_description(html: str, title: str, raw_name: str) -> str:
    if not html:
        return ""
    aliases = {title.lower(), raw_name.lower(), f"xl | {title}".lower()}
    keep: list[str] = []
    for chunk in re.findall(r"(?is)<p>(.*?)</p>", html) or [html]:
        text = re.sub(r"<[^>]+>", " ", chunk)
        text = unescape(text)
        text = re.sub(r"\s+", " ", text).strip(" \t-–—:")
        if not text or text.lower() in aliases:
            continue
        if re.fullmatch(r"(tiktok( video)?|video|link|click here|see more|10% commissionable|please ensure that this is always shared with your teams and itc.?s?)", text, re.I):
            continue
        if "booked via these special links" in text.lower():
            continue
        keep.append(f"<p>{text}</p>")
    return "".join(keep)


def is_public(item: dict, now: datetime) -> bool:
    if not isinstance(item, dict) or item.get("isDeleted"):
        return False
    cid = item.get("id")
    if cid in FEATURED_IDS:
        return False
    if not promotion_assets(item):
        return False
    end = parse_dt(item.get("specialsEnd"))
    if end and end <= now:
        return False
    if not end and item.get("isActive") is False:
        return False
    return True


def assert_no_hq_leak(payload: str, where: str) -> None:
    low = payload.lower()
    if "xltravel.co.za" in low:
        raise SystemExit(f"Refusing to publish: {where} still contains xltravel.co.za")
    if "travelfind.me" in low:
        raise SystemExit(f"Refusing to publish: {where} still contains a TravelFind URL")


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


def publish_images(campaign_id: object, assets: list[dict], img_root: Path, skip_download: bool) -> list[str]:
    folder = img_root / str(campaign_id)
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
        rels.append(f"assets/img/specials/hq/{campaign_id}/{filename}")
    keep = {row["file"] for row in written}
    for leftover in folder.glob("*"):
        if leftover.name != "manifest.json" and leftover.name not in keep:
            leftover.unlink()
    manifest_path.write_text(json.dumps({"images": written}, indent=2) + "\n", encoding="utf-8")
    return rels


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
    for cid, label in CATEGORIES:
        print(f"Fetching {label} ({cid}) …")
        data = http_get_json(f"{CATEGORY_URL}/{cid}")
        items = data if isinstance(data, list) else (data.get("content") or data.get("data") or [])
        public = [it for it in items if is_public(it, now)]
        print(f"  {len(items)} raw, {len(public)} public with flyers")
        chosen.extend(public)

    chosen.sort(key=lambda it: parse_dt(it.get("specialsEnd")) or datetime.max.replace(tzinfo=timezone.utc))
    if dry_run:
        for it in chosen:
            print(f"  - {it.get('id')} {clean_title(it.get('name') or '')} ({len(promotion_assets(it))} images)")
        return {"count": len(chosen), "dry_run": True}

    data_dir = SITE_ROOT / "assets" / "data"
    img_root = SITE_ROOT / "assets" / "img" / "specials" / "hq"
    data_dir.mkdir(parents=True, exist_ok=True)
    img_root.mkdir(parents=True, exist_ok=True)

    campaigns = []
    for it in chosen:
        title = clean_title(it.get("name") or f"Campaign {it.get('id')}")
        print(f"  publishing {it.get('id')} {title}")
        end = parse_dt(it.get("specialsEnd"))
        desc = tidy_description(sanitize_description(it.get("description")), title, it.get("name") or "")
        images = publish_images(it["id"], promotion_assets(it), img_root, skip_download)
        card = {
            "id": it.get("id"),
            "slug": slugify(title, it.get("id")),
            "title": title,
            "ends": end.isoformat() if end else None,
            "ends_label": end.strftime("%d %b %Y") if end else None,
            "description_html": desc,
            "images": images,
        }
        assert_no_hq_leak(json.dumps(card, ensure_ascii=False), f"campaign {card['id']}")
        campaigns.append(card)

    payload = {"generated_at": now.isoformat(), "count": len(campaigns), "campaigns": campaigns}
    raw = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    assert_no_hq_leak(raw, "specials.json")
    (data_dir / "specials.json").write_text(raw, encoding="utf-8")

    keep = {str(c["id"]) for c in campaigns}
    if img_root.is_dir():
        for child in img_root.iterdir():
            if child.is_dir() and child.name not in keep:
                shutil.rmtree(child)
                print(f"  removed expired {child.name}")

    update_sitemap(now.strftime("%Y-%m-%d"))
    print(f"Wrote {data_dir / 'specials.json'} ({len(campaigns)} campaigns)")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sync HQ flyers onto the specials page")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-download", action="store_true")
    args = parser.parse_args(argv)
    run(dry_run=args.dry_run, skip_download=args.skip_download)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
