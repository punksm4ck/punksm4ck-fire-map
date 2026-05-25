# Aegis Omni-Tracker

**Real-time US industrial fire intelligence dashboard with live map tracking, RSS feed ingestion, and heuristic analysis.**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey)

---

## Overview

Aegis Omni-Tracker is a desktop intelligence tool that monitors and maps US industrial fire incidents in near-real-time. It pulls live RSS feeds from Google News, auto-geocodes locations extracted from headlines, and renders them as interactive map markers — all inside a dark-themed Tkinter GUI.

Originally built to track post-April 2026 US industrial fire incidents, the architecture is general enough to adapt to any localized news-monitoring use case.

---

## Features

- 🗺️ **Interactive Map** — Google Maps tile-backed map via `tkintermapview`, centered on the continental US
- 📡 **Live RSS Ingestion** — Pulls from Google News every 15 minutes; deduplicates by URL
- 📍 **Auto-Geocoding** — Regex extracts location strings from headlines and geocodes via OpenStreetMap (Nominatim)
- 🔥 **Seeded Incident Database** — Pre-loaded with verified incidents; persists new finds to a local JSON cache
- 📊 **Heuristic Analysis Panel** — Live stats: total incidents, states affected, suspected arson count, primary hotspot
- 📰 **Intel Feed** — Scrollable treeview of scraped headlines; double-click or right-click to open source URL
- 💾 **Local JSON Cache** — All markers and news items persisted to `aegis_omni_db.json` alongside the script

---

## Screenshots

> *(Add screenshots here once deployed)*

---

## Requirements

- Python 3.8+
- See [`requirements.txt`](requirements.txt) for all dependencies

### System dependencies (Linux)

```bash
sudo apt install python3-tk
```

---

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/aegis-omni-tracker.git
cd aegis-omni-tracker
pip install -r requirements.txt
python aegis_fire_map.py
```

---

## Usage

| Action | Result |
|---|---|
| Launch script | Opens GUI, loads seed data, triggers first sync |
| **Force Omni-Sync** button | Manually triggers an RSS pull cycle |
| **Show Intelligence Feed** button | Toggles the live headline panel |
| Double-click a headline | Opens source article in browser |
| Right-click a headline | Context menu → Open Intel Link |

The app auto-syncs every **15 minutes** and appends any new incidents to the local cache.

---

## Data Persistence

Aegis writes a `aegis_omni_db.json` file to the same directory as the script. This file stores:

- All map markers (city, lat/lon, description)
- All scraped news items (title, link, date, source)

On each launch, seed markers are merged with any existing cache — no duplicates.

---

## Configuration

All tuneable values are at the top of `aegis_fire_map.py`:

| Variable | Default | Description |
|---|---|---|
| `self.root.geometry` | `1600x900` | Window size |
| `target_url` | Google News RSS | Feed URL; swap for any RSS source |
| `self.root.after(900000, ...)` | 15 min | Sync interval in milliseconds |
| `set_position` | `39.8283, -98.5795` | Initial map center (US centroid) |
| `set_zoom` | `4` | Initial zoom level |

---

## Repo Structure

```
aegis-omni-tracker/
├── aegis_fire_map.py       # Main application
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── CHANGELOG.md            # Version history
├── CONTRIBUTING.md         # Contribution guidelines
├── LICENSE                 # MIT License
├── .gitignore              # Excludes cache and backup files
└── docs/
    └── ARCHITECTURE.md     # Technical deep-dive
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT — see [LICENSE](LICENSE).
