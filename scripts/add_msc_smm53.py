#!/usr/bin/env python3
"""Insert the MSC Cruises SMM53 brand campaign (no from-prices) onto specials.html."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SPECIALS = ROOT / "specials.html"
SITEMAP = ROOT / "sitemap.xml"
README = ROOT / "README.md"

MSC_SECTION = """<section class=\"special-section\" id=\"msc\">
<div class=\"special-section-head reveal\">
<div class=\"special-section-copy\">
<span class=\"section-kicker\">MSC Cruises \u00b7 XL Travel SMM53</span>
<h2>There's more to life at sea</h2>
<p>Lose track of the ordinary, discover the extraordinary. MSC Cruises across new horizons, flavours, family time and island escapes. No from-prices on this campaign - ask XL Highway Travel to quote your dates, cabin and itinerary. Flights, visas and insurance excluded unless arranged. SADC residents. E&OE.</p>
</div>
<div class=\"special-section-media\">
<img src=\"assets/img/specials/pdf-only/msc-armonia.webp\" alt=\"MSC cruise ship at a private island\" width=\"1080\" height=\"1080\" loading=\"lazy\">
</div>
</div>
<div class=\"deal-grid\">
<article class=\"deal-card reveal\">
<div class=\"deal-card-media\">
<img src=\"assets/img/specials/pdf-only/msc-mediterranean.webp\" alt=\"Mediterranean port and historic city on an MSC cruise\" width=\"1080\" height=\"1080\" loading=\"lazy\">
<span class=\"deal-save\">Discover</span>
</div>
<div class=\"deal-card-body\">
<span class=\"brand\">New horizons</span>
<h3>More to discover</h3>
<p class=\"meta\">New places and new stories. Ask us to quote Mediterranean, Caribbean and worldwide MSC itineraries.</p>
<a class=\"btn btn-secondary\" href=\"contact.html?interest=MSC%20Cruises%20discover\">Enquire</a>
</div>
</article>
<article class=\"deal-card reveal\">
<div class=\"deal-card-media\">
<img src=\"assets/img/specials/pdf-only/msc-newyear.webp\" alt=\"Dining and celebration onboard MSC Cruises\" width=\"1080\" height=\"1080\" loading=\"lazy\">
<span class=\"deal-save\">Savour</span>
</div>
<div class=\"deal-card-body\">
<span class=\"brand\">Flavours from around the world</span>
<h3>More to savour</h3>
<p class=\"meta\">Long lunches and late dinners at sea. We quote dining, drinks packages and cabin category with your sailing.</p>
<a class=\"btn btn-secondary\" href=\"contact.html?interest=MSC%20Cruises%20savour\">Enquire</a>
</div>
</article>
<article class=\"deal-card reveal\">
<div class=\"deal-card-media\">
<img src=\"assets/img/specials/pdf-only/msc-christmas.webp\" alt=\"Family time on an MSC cruise\" width=\"1080\" height=\"1080\" loading=\"lazy\">
<span class=\"deal-save\">Share</span>
</div>
<div class=\"deal-card-body\">
<span class=\"brand\">Family moments</span>
<h3>More to share</h3>
<p class=\"meta\">More reasons to laugh together. Family cabins and kids clubs quoted for your dates.</p>
<a class=\"btn btn-secondary\" href=\"contact.html?interest=MSC%20Cruises%20family\">Enquire</a>
</div>
</article>
<article class=\"deal-card reveal\">
<div class=\"deal-card-media\">
<img src=\"assets/img/specials/pdf-only/msc-world-asia.webp\" alt=\"MSC ocean escape to island shores\" width=\"1080\" height=\"1080\" loading=\"lazy\">
<span class=\"deal-save\">Escape</span>
</div>
<div class=\"deal-card-body\">
<span class=\"brand\">Find your way to paradise</span>
<h3>More to escape</h3>
<p class=\"meta\">Leave the everyday behind. Private-island and beach days quoted cruise-only unless you ask us to add flights.</p>
<a class=\"btn btn-secondary\" href=\"contact.html?interest=MSC%20Cruises%20escape\">Enquire</a>
</div>
</article>
</div>
<p class=\"text-muted reveal\" style=\"margin:1rem 0 0;font-size:0.9rem\">Source: XL Travel - <em>SMM53 MSC Brand Campaign</em>. Rates on application; air, visas and insurance excluded; departure taxes and levies subject to change; SADC residents only. E&OE.</p>
</section>"""

JSON_LD = """{
\"@context\":\"https://schema.org\",\"@type\":\"ItemList\",\"name\":\"Current travel specials\",\"url\":\"https://xlhighwaytravel.co.za/specials.html\",\"itemListElement\":[
{\"@type\":\"ListItem\",\"position\":1,\"name\":\"Uniworld luxury river cruising\",\"url\":\"https://xlhighwaytravel.co.za/specials.html#uniworld\"},
{\"@type\":\"ListItem\",\"position\":2,\"name\":\"Club Med Phuket\",\"url\":\"https://xlhighwaytravel.co.za/specials.html#phuket\"},
{\"@type\":\"ListItem\",\"position\":3,\"name\":\"Bakubung and Kwa Maritane Pilanesberg\",\"url\":\"https://xlhighwaytravel.co.za/specials.html#bakubung\"},
{\"@type\":\"ListItem\",\"position\":4,\"name\":\"One&Only Cape Town\",\"url\":\"https://xlhighwaytravel.co.za/specials.html#oneonly\"},
{\"@type\":\"ListItem\",\"position\":5,\"name\":\"DSC Transfers\",\"url\":\"https://xlhighwaytravel.co.za/specials.html#dsc-transfers\"},
{\"@type\":\"ListItem\",\"position\":6,\"name\":\"Virgin Atlantic Premium\",\"url\":\"https://xlhighwaytravel.co.za/specials.html#virgin-premium\"},
{\"@type\":\"ListItem\",\"position\":7,\"name\":\"Jumeirah Dubai\",\"url\":\"https://xlhighwaytravel.co.za/specials.html#jumeirah\"},
{\"@type\":\"ListItem\",\"position\":8,\"name\":\"Norwegian Cruise Line\",\"url\":\"https://xlhighwaytravel.co.za/specials.html#ncl\"},
{\"@type\":\"ListItem\",\"position\":9,\"name\":\"MSC Cruises\",\"url\":\"https://xlhighwaytravel.co.za/specials.html#msc\"},
{\"@type\":\"ListItem\",\"position\":10,\"name\":\"Guided tours\",\"url\":\"https://xlhighwaytravel.co.za/specials.html#tours\"},
{\"@type\":\"ListItem\",\"position\":11,\"name\":\"Madagascar all-inclusive\",\"url\":\"https://xlhighwaytravel.co.za/specials.html#madagascar\"},
{\"@type\":\"ListItem\",\"position\":12,\"name\":\"Castleburn\",\"url\":\"https://xlhighwaytravel.co.za/specials.html#castleburn\"},
{\"@type\":\"ListItem\",\"position\":13,\"name\":\"Avis WOW\",\"url\":\"https://xlhighwaytravel.co.za/specials.html#avis\"},
{\"@type\":\"ListItem\",\"position\":14,\"name\":\"Airlink Lanseria-Harare\",\"url\":\"https://xlhighwaytravel.co.za/specials.html#airlink\"}
]}
"""


def patch_specials() -> None:
    text = SPECIALS.read_text(encoding="utf-8")
    if 'id="msc"' in text and "SMM53" in text:
        print("specials.html already has SMM53")
        return

    text = text.replace(
        "Norwegian Cruise Line from R33 700pps, tours, Madagascar, Castleburn, Avis WOW and Airlink Lanseria\u2013Harare",
        "Norwegian Cruise Line from R33 700pps, MSC Cruises, tours, Madagascar, Castleburn, Avis WOW and Airlink Lanseria\u2013Harare",
    )
    if '<span class="deadline-chip">MSC Cruises' not in text:
        text = text.replace(
            '<span class="deadline-chip urgent">NCL Free at Sea sale to 17 Sep 2026</span>',
            '<span class="deadline-chip urgent">NCL Free at Sea sale to 17 Sep 2026</span>\n<span class="deadline-chip">MSC Cruises \u00b7 quote on request</span>',
        )
    text = text.replace(
        '<a href="#ncl">8. Norwegian Cruise Line</a>\n<a href="#tours">9. Guided tours</a>',
        '<a href="#ncl">8. Norwegian Cruise Line</a>\n<a href="#msc">9. MSC Cruises</a>\n<a href="#tours">10. Guided tours</a>',
    )
    text = text.replace('<a href="#madagascar">10. Madagascar</a>', '<a href="#madagascar">11. Madagascar</a>')
    text = text.replace('<a href="#castleburn">11. Castleburn</a>', '<a href="#castleburn">12. Castleburn</a>')
    text = text.replace('<a href="#avis">12. Avis WOW</a>', '<a href="#avis">13. Avis WOW</a>')
    text = text.replace('<a href="#airlink">13. Airlink Harare</a>', '<a href="#airlink">14. Airlink Harare</a>')

    if 'id="msc"' not in text:
        text, n = re.subn(
            r'(</section>\s*)(<!-- LIVE-SPECIALS:START -->|<section class="special-section" id="tours">)',
            r'\1' + MSC_SECTION + '\n\2',
            text,
            count=1,
            flags=re.S,
        )
        # Insert immediately after the NCL section instead.
        if 'id="msc"' not in text:
            text, n = re.subn(
                r'(<section class="special-section" id="ncl">.*?</section>\s*)',
                r'\1' + MSC_SECTION + '\n',
                text,
                count=1,
                flags=re.S,
            )
            if n != 1:
                raise SystemExit(f"could not insert MSC after NCL (n={n})")

    text = text.replace(
        "<strong>Norwegian Cruise Line (SMM52):</strong> 50% off all cruises* plus Free at Sea\u2122; featured inside from-prices from R33 700; cruise only; sales until 17 September 2026; SADC residents only.",
        "<strong>Norwegian Cruise Line (SMM52):</strong> 50% off all cruises* plus Free at Sea\u2122; featured inside from-prices from R33 700; cruise only; sales until 17 September 2026; SADC residents only. "
        "<strong>MSC Cruises (SMM53):</strong> brand campaign; rates on application; cruise only unless quoted otherwise; air, visas and insurance excluded; departure taxes and levies subject to change; peak surcharges, block-outs, advance-purchase and minimum-stay rules may apply; group rates on request; valid for SADC residents; supplier terms apply. E&OE.",
    )

    text, n = re.subn(
        r'<script type="application/ld\+json">\s*\{.*?\}\s*</script>',
        '<script type="application/ld+json">\n' + JSON_LD + '</script>',
        text,
        count=1,
        flags=re.S,
    )
    if n != 1:
        print("warning: json-ld not replaced", n)

    if "<!-- msc-smm53 2026-09-04 -->" not in text:
        text = text.replace(
            "<!-- LIVE-SPECIALS:END -->",
            "<!-- LIVE-SPECIALS:END -->\n<!-- msc-smm53 2026-09-04 -->",
            1,
        )

    if 'id="msc"' not in text or "SMM53" not in text:
        raise SystemExit("MSC SMM53 missing after patch")
    SPECIALS.write_text(text, encoding="utf-8")
    print("updated", SPECIALS)


def patch_sitemap() -> None:
    if not SITEMAP.exists():
        return
    text = SITEMAP.read_text(encoding="utf-8")
    text2, n = re.subn(
        r'(<loc>https://xlhighwaytravel.co.za/specials.html</loc>\s*<lastmod>)[^<]+',
        r'\g<1>2026-09-04',
        text,
        count=1,
    )
    if n:
        SITEMAP.write_text(text2, encoding="utf-8")
        print("updated sitemap lastmod")


def patch_readme() -> None:
    if not README.exists():
        return
    text = README.read_text(encoding="utf-8")
    text2 = text.replace(
        "Cape Town, Jumeirah, Virgin, NCL, Uniworld, Club Med, tours, Avis, Castleburn, One&Only, DSC Transfers, Bakubung / Kwa Maritane",
        "Cape Town, Jumeirah, Virgin, NCL, MSC, Uniworld, Club Med, tours, Avis, Castleburn, One&Only, DSC Transfers, Bakubung / Kwa Maritane",
    )
    if text2 != text:
        README.write_text(text2, encoding="utf-8")
        print("updated README")


if __name__ == "__main__":
    patch_specials()
    patch_sitemap()
    patch_readme()
