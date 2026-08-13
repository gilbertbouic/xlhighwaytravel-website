# XL Highway Travel — Website

Static site for [xlhighwaytravel.co.za](https://xlhighwaytravel.co.za) — hosted on GitHub Pages.

## Live (GitHub Pages)

https://gilbertbouic.github.io/xlhighwaytravel-website/

## Local preview

```bash
python3 -m http.server 8080
```

## Specials sync

Every **Tuesday at 11:00 South Africa time**, a GitHub Action copies current XL Travel HQ specials onto `specials.html` as deal cards. Campaigns already written up on the page (Cape Town, Jumeirah, Virgin, Hurtigruten, tours, Avis, Castleburn) are skipped. The Airlink Lanseria–Harare section is ours and is never replaced.

```bash
python3 scripts/publish_specials.py
python3 scripts/publish_specials.py --dry-run
```

## Brand

Logo preserved. Colours from XL branding palette (`#AB2B2B`, `#FB7F18`, `#8E0D1A`, etc.).
