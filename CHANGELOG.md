# Changelog

All notable changes to Aegis Omni-Tracker are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.1.0] - 2026-04-14

### Fixed
- **SyntaxError** in `default_markers` list — missing trailing comma after Abington Township entry
- **Hardcoded absolute path** (`/home/tsann/Scripts/aegis_omni_db.json`) replaced with portable `os.path` resolution relative to script location

### Changed
- **Auto-geocode regex** updated to handle hyphenated location names (e.g. `Miami-Dade`) and `County`-suffixed places:
  - Before: `r"([A-Z][a-zA-Z\s]+,\s(?:[A-Z]{2}|[A-Z][a-z]+))"`
  - After: `r"([A-Z][a-zA-Z\s\-]+(?:\s*County)?,\s(?:[A-Z]{2}|[A-Z][a-z]+))"`

### Added
- **Miami-Dade County, FL** added to seeded `default_markers`

---

## [1.0.0] - 2026-04-06

### Added
- Initial release
- Interactive map via `tkintermapview` with Google Maps tile server
- Live RSS ingestion from Google News (15-minute auto-sync cycle)
- Auto-geocoding of locations extracted from headlines via OpenStreetMap Nominatim
- Seeded incident database with 12 verified US industrial fire locations
- Heuristic analysis panel (incident count, states affected, arson flags, hotspot zone)
- Intel Feed treeview with double-click / right-click URL launch
- Local JSON persistence (`aegis_omni_db.json`)
- Force Omni-Sync manual refresh button
- Dark theme UI (`#121212` / `#1a1a1a` palette)
