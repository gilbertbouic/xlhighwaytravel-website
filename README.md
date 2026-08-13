# XL Highway Travel — Website

Static site for [xlhighwaytravel.co.za](https://xlhighwaytravel.co.za) — hosted on GitHub Pages.

## Live (GitHub Pages)

https://gilbertbouic.github.io/xlhighwaytravel-website/

## Local preview

```bash
python3 -m http.server 8080
```

## HQ specials sync

A GitHub Action checks XL Travel HQ every **Tuesday at 11:00 South Africa time** and updates the flyer grid on `specials.html`. Customers enquire on this site only.

```bash
python3 scripts/publish_specials.py
python3 scripts/publish_specials.py --dry-run
```

Manual run: GitHub → Actions → **Sync HQ specials** → Run workflow.

## Brand

Logo preserved. Colours from XL branding palette (`#AB2B2B`, `#FB7F18`, `#8E0D1A`, etc.).
