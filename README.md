# XL Highway Travel - Website

Static site for [xlhighwaytravel.co.za](https://xlhighwaytravel.co.za) - hosted on GitHub Pages.

## Live (GitHub Pages)

https://gilbertbouic.github.io/xlhighwaytravel-website/

## Local preview

```bash
python3 -m http.server 8080
```

## Specials sync

Every **Tuesday at 11:00 South Africa time**, a GitHub Action copies current XL Travel HQ specials onto `specials.html` as deal cards. Campaigns already written up on the page (Cape Town, Jumeirah, Virgin, NCL, MSC, Uniworld, Club Med, tours, Avis, Castleburn, One&Only, DSC Transfers, Bakubung / Kwa Maritane) are skipped. The Airlink Lanseria-Harare section is ours and is never replaced.

```bash
python3 scripts/publish_specials.py
python3 scripts/publish_specials.py --dry-run
```

## Search visibility

- Live hostname in this repo is **https://xlhighwaytravel.co.za** (use that in Search Console). In GitHub Pages, turn on **Enforce HTTPS**. If both `www` and the apex resolve, pick one as primary and redirect the other so Google does not split the listing.
- Google verification file: `googlea40fc137780d0ae3.html` (do not add it to the sitemap).
- Submit `https://xlhighwaytravel.co.za/sitemap.xml` in [Google Search Console](https://search.google.com/search-console) and Bing Webmaster Tools.
- Analytics: add a GA4 measurement ID when you have one. Do not invent a tracking snippet. Until then, use Search Console for queries and WhatsApp/email counts for leads.

## Old WordPress URLs

Google still lists pre-migration slugs such as `/contact-form/` and `/t-cs/`. GitHub Pages cannot send a real HTTP 301, so those paths are noindex stubs (canonical + refresh + JavaScript) that send people to the current page. Unknown old URLs hit `404.html`, which uses the same map. Image and attachment leftovers stay as 404s so Google can drop them. Do not add stub folders to the sitemap.

```bash
python3 scripts/write_legacy_redirects.py
```

A true 301 needs DNS in front of GitHub Pages (for example Cloudflare). Until then these stubs are the best the host can do.

## Brand

Logo preserved. Colours from XL branding palette (`#AB2B2B`, `#FB7F18`, `#8E0D1A`, etc.).
