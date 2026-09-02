#!/usr/bin/env python3
"""Add current HQ specials to specials.html as deal cards.

Fetches TravelFind categories 158 and 159. Skips campaigns already written
up on the page (Cape Town, Jumeirah, Virgin, NCL, tours, Avis,
Castleburn, One&Only, DSC Transfers, Bakubung / Kwa Maritane). Airlink is not from HQ and is left untouched.

Usage:
  python3 scripts/publish_specials.py
  python3 scripts/publish_specials.py --dry-run
"""
