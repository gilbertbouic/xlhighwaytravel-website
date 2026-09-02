#!/usr/bin/env python3
"""One-shot editor: drop expired specials and insert the NCL SMM52 sale."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SPECIALS = ROOT / "specials.html"
PUBLISH = ROOT / "scripts" / "publish_specials.py"

NCL_SECTION = """<section class="special-section" id="ncl">
<div class="special-section-head reveal">
<div class="special-section-copy">
<span class="section-kicker">Norwegian Cruise Line · Sales until 17 September 2026</span>
<h2>NCL September sale — 50% off + Free at Sea</h2>
<p>50% off all cruises* plus Free at Sea™: premium beverages, speciality dining, excursion credits and a Wi-Fi package. 3rd and 4th guests pay taxes and fees only on select sailings. Cruise-only inside stateroom from-prices. Flights not included. Additional fees apply*. Book through XL Highway Travel.</p>
</div>
<div class="special-section-media">
<img src="assets/img/specials/pdf-only/ncl-section.webp" alt="Norwegian Cruise Line September sale" width="1080" height="1080" loading="lazy">
</div>
</div>
<div class="deal-grid">
<article class="deal-card reveal">
<div class="deal-card-media">
<img src="assets/img/specials/pdf-only/ncl-florence-mediterranean.webp" alt="Mediterranean cruise to Ibiza and Rome" width="1080" height="1080" loading="lazy">
<span class="deal-save">10 days</span>
</div>
<div class="deal-card-body">
<span class="brand">Norwegian Dawn · Barcelona</span>
<h3>Mediterranean: Ibiza & Rome</h3>
<p class="meta">10-day ocean cruise from Barcelona, 16-26 September 2027. Inside stateroom.</p>
<div class="deal-price"><span class="now">R33 700</span><span class="unit">pps cruise only</span></div>
<a class="btn btn-secondary" href="contact.html?interest=NCL%20Mediterranean%20Ibiza%20Rome">Enquire</a>
</div>
</article>
<article class="deal-card reveal">
<div class="deal-card-media">
<img src="assets/img/specials/pdf-only/ncl-greek-isles.webp" alt="Greek Isles and Italy cruise" width="1080" height="1080" loading="lazy">
<span class="deal-save">8 days</span>
</div>
<div class="deal-card-body">
<span class="brand">Norwegian Viva · Rome</span>
<h3>Greek Isles & Italy</h3>
<p class="meta">Santorini, Athens and Salerno. 8-day cruise from Rome, 28 August-5 September 2027. Inside stateroom.</p>
<div class="deal-price"><span class="now">R36 800</span><span class="unit">pps cruise only</span></div>
<a class="btn btn-secondary" href="contact.html?interest=NCL%20Greek%20Isles%20Italy">Enquire</a>
</div>
</article>
<article class="deal-card reveal">
<div class="deal-card-media">
<img src="assets/img/specials/pdf-only/ttc-portugal-lisbon.webp" alt="British Isles cruise" width="1080" height="1080" loading="lazy">
<span class="deal-save">11 days</span>
</div>
<div class="deal-card-body">
<span class="brand">Norwegian Star · Southampton</span>
<h3>British Isles</h3>
<p class="meta">England, Ireland and Scotland. 11-day cruise from Southampton, 23 July-3 August 2027. Inside stateroom.</p>
<div class="deal-price"><span class="now">R52 600</span><span class="unit">pps cruise only</span></div>
<a class="btn btn-secondary" href="contact.html?interest=NCL%20British%20Isles">Enquire</a>
</div>
</article>
<article class="deal-card reveal">
<div class="deal-card-media">
<img src="assets/img/specials/pdf-only/msc-world-asia.webp" alt="Asia cruise from Tokyo" width="1080" height="1080" loading="lazy">
<span class="deal-save">14 days</span>
</div>
<div class="deal-card-body">
<span class="brand">Norwegian Jade · Tokyo</span>
<h3>Asia: Hakodate, Hiroshima & Kochi</h3>
<p class="meta">14-day ocean cruise from Tokyo, 4-18 November 2027. Inside stateroom.</p>
<div class="deal-price"><span class="now">R61 800</span><span class="unit">pps cruise only</span></div>
<a class="btn btn-secondary" href="contact.html?interest=NCL%20Asia%20Tokyo">Enquire</a>
</div>
</article>
</div>
<p class="text-muted reveal" style="margin:1rem 0 0;font-size:0.9rem">Source: XL Travel - <em>SMM52 DP NCL Sep Sale</em>. Cruise-only inside from-prices; flights excluded; sales until 17 September 2026; SADC residents only. E&OE.</p>
</section>"""


def drop_section(text: str, section_id: str) -> str:
    pattern = rf'<section class="special-section" id="{section_id}">.*?</section>\s*'
    updated, n = re.subn(pattern, "", text, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f"section {section_id} count {n}")
    return updated


def patch_publish() -> None:
    text = PUBLISH.read_text(encoding="utf-8")
    text = text.replace(
        "Cape Town, Jumeirah, Virgin, Hurtigruten, tours, Avis,",
        "Cape Town, Jumeirah, Virgin, NCL, tours, Avis,",
    )
    text = text.replace(
        "hurtigruten|development promotions",
        "hurtigruten|norwegian cruise|\\bncl\\b|development promotions",
    )
    if "def run(" not in text:
        raise SystemExit("publish_specials.py is incomplete")
    PUBLISH.write_text(text, encoding="utf-8")


def patch_specials() -> None:
    text = SPECIALS.read_text(encoding="utf-8")
    if 'id="ncl"' in text and 'id="hurtigruten"' not in text and 'id="cape-town"' not in text:
        print("specials.html already pruned")
        return
    text = text.replace(
        "Cape Town winter stays, Virgin Atlantic Premium, MSC cruises, Jumeirah Dubai from R44 130pps, Hurtigruten, tours,",
        "Virgin Atlantic Premium, Jumeirah Dubai from R44 130pps, Norwegian Cruise Line from R33 700pps, tours,",
    )
    text = re.sub(r'<span class="deadline-chip urgent">Cape Town winter stays to 31 Aug 2026</span>\s*', "", text)
    text = re.sub(r'<span class="deadline-chip urgent">MSC Cruises sales to 31 Aug 2026</span>\s*', "", text)
    text = text.replace(
        '<span class="deadline-chip urgent">Hurtigruten sales to 31 Aug 2026</span>',
        '<span class="deadline-chip urgent">NCL Free at Sea sale to 17 Sep 2026</span>',
    )
    text = re.sub(r'<a href="#cape-town">6\. Cape Town winter</a>\s*', "", text)
    text = text.replace('<a href="#virgin-premium">7. Virgin Atlantic Premium</a>', '<a href="#virgin-premium">6. Virgin Atlantic Premium</a>')
    text = text.replace('<a href="#jumeirah">8. Jumeirah Dubai</a>', '<a href="#jumeirah">7. Jumeirah Dubai</a>')
    text = text.replace('<a href="#hurtigruten">9. Hurtigruten</a>', '<a href="#ncl">8. Norwegian Cruise Line</a>')
    text = re.sub(r'<a href="#msc">10\. MSC Cruises</a>\s*', "", text)
    text = text.replace('<a href="#tours">11. Guided tours</a>', '<a href="#tours">9. Guided tours</a>')
    text = text.replace('<a href="#madagascar">12. Madagascar</a>', '<a href="#madagascar">10. Madagascar</a>')
    text = text.replace('<a href="#castleburn">13. Castleburn</a>', '<a href="#castleburn">11. Castleburn</a>')
    text = text.replace('<a href="#avis">14. Avis WOW</a>', '<a href="#avis">12. Avis WOW</a>')
    text = text.replace('<a href="#airlink">15. Airlink Harare</a>', '<a href="#airlink">13. Airlink Harare</a>')
    text = drop_section(text, "cape-town")
    text = re.sub(
        r'<section class="special-section" id="hurtigruten">.*?</section>\s*',
        NCL_SECTION + "\n",
        text,
        count=1,
        flags=re.S,
    )
    if 'id="hurtigruten"' in text:
        raise SystemExit("hurtigruten still present")
    text = drop_section(text, "msc")
    text = text.replace(
        "<strong>Hurtigruten (SMM43):</strong> inside cabin from-prices; sales until 31 Aug 2026; flights excluded; Northern Lights Promise on qualifying sailings 20 Sep 2026 – 31 Mar 2027 (11+ days).",
        "<strong>Norwegian Cruise Line (SMM52):</strong> 50% off all cruises* plus Free at Sea™; featured inside from-prices from R33 700; cruise only; sales until 17 September 2026; SADC residents only.",
    )
    text = re.sub(r'<strong>MSC Cruises:</strong>.*?(?=\n<strong>| Visas)', "", text, count=1, flags=re.S)
    text = text.replace(
        " <strong>Cape Town Legacy (Portswood & Commodore):</strong> land-only from-prices per night; breakfast included; minimum 3 nights; sales until 31 Aug 2026; stay 1 Jun – 31 Aug 2026; SADC residents.",
        "",
    )
    if 'id="cape-town"' in text or 'id="hurtigruten"' in text or 'id="msc"' in text or 'id="ncl"' not in text:
        raise SystemExit("sanity check failed")
    SPECIALS.write_text(text, encoding="utf-8")
    print("updated", SPECIALS)


if __name__ == "__main__":
    patch_publish()
    patch_specials()
