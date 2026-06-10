# Architecture

Technical reference for Aegis Omni-Tracker.

---

## High-Level Flow

```
Launch
  │
  ├─ init_ui()          Build Tkinter layout, panels, treeview, map widget
  │
  ├─ recover_database() Load or create aegis_omni_db.json
  │     ├─ Merge default_markers into cache (city-key dedup)
  │     ├─ render_map()
  │     ├─ render_news()
  │     └─ update_heuristics()
  │
  └─ trigger_update_cycle()   Spawns background thread every 15 min
        └─ execute_omni_pull()
              ├─ Fetch Google News RSS
              ├─ Parse XML → extract title, link, date, source
              ├─ Dedup by URL → append new items to db["news"]
              ├─ extract_and_geocode(title) for each new item
              │     ├─ Regex extract location string
              │     └─ geocoder.osm() → append to db["markers"]
              ├─ Sort news by date desc
              ├─ secure_database() → write aegis_omni_db.json
              └─ Schedule UI refresh via root.after(0, ...)
```

---

## Key Classes & Methods

### `AegisOmniTracker`

Single class; owns all state and UI.

| Method | Responsibility |
|---|---|
| `__init__` | Wire root window, initialize db, call init chain |
| `init_ui` | Build all Tkinter widgets and layout |
| `recover_database` | Load JSON cache, merge seeds, trigger initial render |
| `secure_database` | Write current `self.db` state to JSON file |
| `render_map` | Clear and re-place all markers on the map widget |
| `render_news` | Clear and repopulate the treeview from `db["news"]` |
| `update_heuristics` | Recompute and push stat panel values |
| `execute_omni_pull` | Background thread: fetch RSS, geocode, persist |
| `extract_and_geocode` | Regex + OSM geocoder for a single headline string |
| `trigger_update_cycle` | Kick off background thread + schedule next cycle |
| `toggle_feed` | Show/hide the Intel Feed panel |
| `launch_source_url` | Open URL from treeview double-click |
| `launch_from_menu` | Open URL from right-click context menu |

---

## Data Model

### `self.db` (in-memory, mirrored to `aegis_omni_db.json`)

```json
{
  "markers": [
    {
      "city": "Ontario, CA",
      "lat": 34.0633,
      "lon": -117.6509,
      "desc": "Kimberly-Clark Warehouse (Arson)"
    }
  ],
  "news": [
    {
      "title": "Warehouse fire breaks out in...",
      "link": "https://...",
      "date": "Tue, 08 Apr 2026 14:32:00 GMT",
      "source": "Los Angeles Times"
    }
  ]
}
```

**Deduplication keys:**
- Markers: `city` string (exact match)
- News items: `link` URL (exact match)

---

## Geocoding

Location strings are extracted from headlines using:

```python
re.search(r"([A-Z][a-zA-Z\s\-]+(?:\s*County)?,\s(?:[A-Z]{2}|[A-Z][a-z]+))", title)
```

This matches patterns like:
- `"Ontario, CA"`
- `"Wayne County, OH"`
- `"Miami-Dade County, FL"`
- `"St. Louis, Missouri"` *(partial — lowercase state names not matched)*

Geocoding is performed via `geocoder.osm()` (OpenStreetMap Nominatim). Nominatim has a **1 req/sec** rate limit per its usage policy. High-frequency sync cycles on large feeds may hit this limit — consider adding a `time.sleep(1)` between geocode calls if you expand the feed volume.

---

## Threading Model

`execute_omni_pull` runs in a `daemon=True` thread to keep the UI responsive during network I/O. All UI mutations are marshalled back to the main thread via `self.root.after(0, callback)` — direct widget calls from background threads will crash Tkinter.

---

## Known Limitations

- **Regex geocoding is best-effort** — headlines with unusual formatting, city names that don't start with a capital, or non-US locations will be skipped
- **Nominatim rate limit** — mass geocoding will be throttled; OSM may temporarily block requests
- **Google News RSS** — the feed structure and availability can change without notice; the app falls back to local cache on any network failure
- **Single-file design** — intentional for portability; refactor into modules only if the feature set grows substantially
