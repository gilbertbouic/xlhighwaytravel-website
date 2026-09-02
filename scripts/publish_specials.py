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
    r"jumeirah|thompsons|virgin atlantic|hurtigruten|norwegian cruise|\\bncl\\b|development promotions|"
    r"\\bavis\\b|castleburn|legacy hotels|portswood|commodore|"
    r"bakubung|bakubang|kwa.?maritane|pilanesberg|one.?only|dsc transfers|"
    r"\\bttc\\b|trafalg|costsaver|insight vacation|madagascar|\\bmsc\\b",
    re.I,
)

MAX_IMAGE_WIDTH = 1400
WEBP_QUALITY = 82
MAX_CARDS = 4
PRICE_RE = re.compile(r"R\\s*([0-9]{1,3}(?:[\\s,][0-9]{3})+|[0-9]{3,})")
