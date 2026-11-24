import csv
import json
import math
import os
import sys
import urllib.request
import webbrowser
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

if "QT_QUICK_BACKEND" in os.environ:
    del os.environ["QT_QUICK_BACKEND"]

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox --ignore-gpu-blocklist --enable-gpu-rasterization --enable-webgl --disable-dev-shm-usage"

from PyQt6.QtCore import Qt, QThread, QTimer, QUrl, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMainWindow, QPushButton, QSizePolicy, QSplitter,
    QTableWidget, QTableWidgetItem, QTabWidget, QTextEdit, QToolBar,
    QVBoxLayout, QWidget
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

USER_COORDS = (39.8283, -98.5795)

def detect_user_location():
    global USER_COORDS
    for url in ("https://ipinfo.io/json", "http://ip-api.com/json/"):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Punksm4ck-Fire-Command/2.0"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                if "loc" in data and "," in str(data["loc"]):
                    lat_s, lng_s = str(data["loc"]).split(",", 1)
                    USER_COORDS = (float(lat_s), float(lng_s))
                    return USER_COORDS
                if "lat" in data and "lon" in data:
                    USER_COORDS = (float(data["lat"]), float(data["lon"]))
                    return USER_COORDS
        except Exception:
            continue
    return USER_COORDS

@dataclass
class FireIncident:
    id: str
    name: str
    city: str
    state: str
    lat: float
    lng: float
    date: str
    category: str
    source: str
    damage: str
    note: str

    def distance_miles(self, origin=None):
        if origin is None:
            origin = USER_COORDS
        r = 3958.8
        phi1, phi2 = math.radians(origin[0]), math.radians(self.lat)
        dphi = math.radians(self.lat - origin[0])
        dlam = math.radians(self.lng - origin[1])
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
        return round(r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 1)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "lat": self.lat,
            "lng": self.lng,
            "date": self.date,
            "category": self.category,
            "source": self.source,
            "damage": self.damage,
            "note": self.note,
            "distance_mi": self.distance_miles()
        }

VERIFIED_INCIDENTS = [
    FireIncident("ca-ontario-kc", "Kimberly-Clark Distribution Center", "Ontario", "CA", 34.0185, -117.5960, "2026-04-07", "Arson", "Federal Prosecutors / AP", "$600M Total Loss", "1.2M sq ft 6-alarm fire; 175 firefighters; employee charged with arson."),
    FireIncident("ca-tracy-medline", "Medline Medical Supply Warehouse", "Tracy", "CA", 37.7397, -121.4252, "2026-06-11", "Warehouse", "The Guardian / AP", "Total Loss / Evacuations", "Broken warehouse sprinkler system & low hydrant pressure hindered firefight."),
    FireIncident("ca-la-lineage", "Lineage Cold Storage Warehouse", "Los Angeles", "CA", 34.0242, -118.2112, "2026-06-17", "Industrial", "CalMatters / LAFD", "5-Day Blaze / Emergency", "Boyle Heights cold storage fire triggered state emergency & hazmat smoke evacuations."),
    FireIncident("tx-houston-cleanharbors", "Clean Harbors Hazardous Waste Plant", "La Porte", "TX", 29.6658, -95.0194, "2026-11-17", "Hazmat", "Local Fire / News", "1 Hospitalized / Blast", "Explosion & fire at industrial hazardous waste treatment plant shattered area windows."),
    FireIncident("ms-washco-chem", "Washington County Chemical Plant", "Greenville", "MS", 33.4101, -91.0618, "2026-11-05", "Hazmat", "JOIFF / EOC", "Shelter-in-Place", "Chemical plant explosion and fire prompted county shelter-in-place order."),
    FireIncident("wa-longview-nippon", "Nippon Dynawave Packaging Plant", "Longview", "WA", 46.1382, -122.9382, "2026-05-26", "CSB", "U.S. CSB Active", "Fatal Incident", "CSB federal investigation opened May 27, 2026 into fatal industrial tank collapse."),
    FireIncident("wv-institute-catalyst", "Catalyst Refiners Chemical Facility", "Institute", "WV", 38.3812, -81.7712, "2026-04-22", "CSB", "U.S. CSB Active", "Fatal H2S Release", "CSB investigating fatal hydrogen sulfide chemical release."),
    FireIncident("me-baileyville-woodland", "Woodland Pulp LLC Mill", "Baileyville", "ME", 45.1592, -67.4022, "2026-01-27", "CSB", "U.S. CSB Active", "Fatal Toxic Gas", "CSB investigating fatal hydrogen sulfide release at manufacturing mill."),
    FireIncident("pa-monaca-shell", "Shell Polymers Petrochemical Plant", "Monaca", "PA", 40.6865, -80.2731, "2026-09-16", "CSB", "U.S. CSB Final Report", "Furnace Explosion", "CSB final report released Sep 2026 on ethane cracking furnace explosion and fire."),
    FireIncident("pa-clairton-ussteel", "U.S. Steel Clairton Coke Works", "Clairton", "PA", 40.2923, -79.8814, "2026-08-10", "CSB", "U.S. CSB Final Report", "2 Fatalities", "CSB final report released Aug 2026 on coke oven gas explosion."),
    FireIncident("ga-conyers-biolab", "Bio-Lab Inc. Chemical Warehouse", "Conyers", "GA", 33.6676, -84.0177, "2026-07-21", "CSB", "U.S. CSB Final Report", "Massive Toxic Plume", "CSB final report released Jul 2026 on chemical warehouse fire and plume."),
    FireIncident("tn-mcewen-aes", "Accurate Energetic Systems Plant", "McEwen", "TN", 36.1089, -87.6347, "2025-10-10", "CSB", "U.S. CSB Active", "Fatal Explosion", "Active 2026 CSB investigation into explosive manufacturing plant blast."),
    FireIncident("nj-newark-lister", "Lister Ave Warehouse Complex", "Newark", "NJ", 40.7357, -74.1724, "2026-04-12", "Warehouse", "Local Fire / OmniDB", "Major Structure Fire", "Multi-alarm industrial warehouse complex fire."),
    FireIncident("oh-westjeff-amazon", "Amazon Warehouse (Solar Fire)", "West Jefferson", "OH", 39.9442, -83.2691, "2026-04-15", "Warehouse", "Local Fire / OmniDB", "Rooftop Solar Fire", "Solar panel array fire on large logistics distribution center."),
    FireIncident("ny-queens-collegept", "College Point Lumberyard & Warehouse", "Queens", "NY", 40.7834, -73.8464, "2026-04-18", "Warehouse", "FDNY / OmniDB", "Multi-Alarm Fire", "Heavy timber and warehouse fire in College Point industrial corridor."),
    FireIncident("ca-bakersfield-recyc", "Warehouse near Recycling Center", "Bakersfield", "CA", 35.3733, -119.0187, "2026-04-20", "Industrial", "Kern County Fire", "Structure Loss", "Abandoned warehouse blaze adjacent to recycling operations."),
    FireIncident("ri-eprov-aspen", "Aspen Aerogels Manufacturing Plant", "East Providence", "RI", 41.8137, -71.3701, "2026-04-22", "Hazmat", "Local Fire / OmniDB", "Industrial Fire", "Fire at aerogel insulation manufacturing facility."),
    FireIncident("il-bedford-ingredion", "Ingredion Food Processing Plant", "Bedford Park", "IL", 41.7611, -87.8017, "2026-04-24", "Industrial", "Local Fire / OmniDB", "Plant Fire", "Industrial fire at major food ingredient processing facility."),
    FireIncident("oh-wayne-southwood", "Southwood Lumber Pallet Factory", "Wooster", "OH", 40.8300, -81.9332, "2026-04-26", "Industrial", "Local Fire / OmniDB", "Factory Loss", "High-fuel-load lumber and wooden pallet factory fire."),
    FireIncident("pa-bethlehem-trash", "Bethlehem Commercial Trash Station", "Bethlehem", "PA", 40.6259, -75.3705, "2026-04-27", "Industrial", "Local Fire / OmniDB", "Transfer Station Fire", "Commercial waste transfer station fire."),
    FireIncident("ga-gwinnett-trash", "Gwinnett Commercial Trash Station", "Lawrenceville", "GA", 33.9526, -84.0203, "2026-04-28", "Industrial", "Local Fire / OmniDB", "Transfer Station Fire", "Commercial waste facility blaze."),
    FireIncident("mi-detroit-aevitas", "Aevitas Specialty Services Recycling", "Detroit", "MI", 42.3314, -83.0458, "2026-04-29", "Hazmat", "Detroit Fire / OmniDB", "Hazmat Recycling Fire", "Specialty recycling and industrial waste facility fire."),
    FireIncident("pa-abington-sps", "SPS Technologies Aerospace Factory", "Abington Township", "PA", 40.1215, -75.1196, "2026-04-30", "Industrial", "Local Fire / OmniDB", "Major Factory Fire", "Massive industrial fire at aerospace fastener manufacturing plant."),
    FireIncident("fl-miami-ind", "Miami-Dade Industrial Complex Fire", "Miami", "FL", 25.7617, -80.1918, "2026-05-02", "Warehouse", "MDFR / OmniDB", "Multi-Alarm Fire", "Large commercial/industrial warehouse blaze in Miami-Dade County.")
]

STYLE = """
QMainWindow { background: #010409; }
QToolBar { background: #0d1117; border-bottom: 1px solid #30363d; padding: 5px; spacing: 6px; }
QStatusBar { background: #0d1117; border-top: 1px solid #30363d; color: #8b949e; font-size: 11px; font-weight: bold; }
QLabel { color: #c9d1d9; font-family: Menlo; }
QPushButton { background: #161b22; border: 1px solid #30363d; border-radius: 6px; color: #e6edf3; padding: 5px 10px; font-size: 11px; font-weight: 600; }
QPushButton:hover { background: #21262d; border-color: #00e5ff; }
QPushButton:checked { background: rgba(0, 229, 255, 0.16); color: #00e5ff; border-color: #00e5ff; }
QLineEdit, QComboBox { background: #0d1117; border: 1px solid #30363d; border-radius: 6px; color: #f0f6fc; padding: 4px 8px; font-size: 11px; }
QFrame[objectName="Dashboard"] { background: #0d1117; border-bottom: 1px solid #30363d; }
QFrame[objectName="KpiCard"] { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 4px 10px; }
QTableWidget { background: #0d1117; color: #e6edf3; gridline-color: #21262d; border: none; font-size: 11px; selection-background-color: rgba(255, 106, 0, 0.25); }
QHeaderView::section { background: #161b22; color: #00e5ff; border: 1px solid #21262d; padding: 5px; font-size: 10px; font-weight: bold; }
QTextEdit { background: #161b22; color: #e6edf3; border: 1px solid #30363d; border-radius: 6px; font-size: 11px; padding: 6px; }
QTabWidget::pane { border: 1px solid #30363d; background: #0d1117; }
QTabBar::tab { background: #161b22; color: #8b949e; padding: 6px 12px; border: 1px solid #30363d; font-size: 11px; font-weight: bold; }
QTabBar::tab:selected { background: #0d1117; color: #ff6a00; border-bottom-color: #ff6a00; }
.DashLabel { color: #8b949e; font-size: 9px; font-weight: bold; letter-spacing: 1px; }
.DashValue { color: #ffffff; font-size: 18px; font-weight: bold; }
.DashOrange { color: #ff6a00; font-size: 18px; font-weight: bold; }
.DashCyan { color: #00e5ff; font-size: 18px; font-weight: bold; }
.DashPink { color: #ff2e93; font-size: 18px; font-weight: bold; }
.DashPurple { color: #b366ff; font-size: 18px; font-weight: bold; }
"""

class NewsSyncWorker(QThread):
    finished = pyqtSignal(list, str)

    def run(self):
        detect_user_location()
        articles = []
        feeds = [
            "https://news.google.com/rss/search?q=%22warehouse+fire%22+OR+%22industrial+fire%22+US+when:30d&hl=en-US&gl=US&ceid=US:en",
            "https://news.google.com/rss/search?q=%22chemical+plant+explosion%22+OR+%22factory+fire%22+US+when:30d&hl=en-US&gl=US&ceid=US:en"
        ]
        seen = set()
        for url in feeds:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Punksm4ck-Fire-Command/2.0"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    xml_data = resp.read()
                root = ET.fromstring(xml_data)
                for item in root.findall(".//item")[:25]:
                    title = (item.findtext("title") or "").strip()
                    link = (item.findtext("link") or "").strip()
                    pub = (item.findtext("pubDate") or "").strip()[:16]
                    src = (item.findtext("source") or "News Wire").strip()
                    if title and title not in seen:
                        seen.add(title)
                        articles.append({"date": pub, "title": title, "source": src, "link": link})
            except Exception:
                continue
        msg = f"Live Wire Synced: {len(articles)} recent US fire reports ({datetime.now().strftime('%H:%M:%S')})"
        self.finished.emit(articles, msg)

class FireCommandWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Punksm4ck Industrial & Warehouse Fire Command — 2026 Edition")
        self.resize(1680, 960)
        self.setStyleSheet(STYLE)
        self.incidents = list(VERIFIED_INCIDENTS)
        self.filtered = list(self.incidents)
        self.news_items = []
        self.map_ready = False
        self.kpi_labels = {}
        self._build_ui()
        self._tick_clock()
        QTimer.singleShot(600, self._sync_live)

    def _build_ui(self):
        tb = self.addToolBar("Main")
        tb.setMovable(False)

        title = QLabel("  ⬡  FIRE INTEL COMMAND  ")
        title.setStyleSheet("color: #ff6a00; font-weight: 800; font-size: 13px;")
        tb.addWidget(title)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Filter city, plant, CSB, arson...")
        self.search.setFixedWidth(220)
        self.search.textChanged.connect(self._apply_filters)
        tb.addWidget(self.search)

        self.state_filter = QComboBox()
        self.state_filter.setFixedWidth(80)
        self.state_filter.addItem("ALL")
        for st in sorted({i.state for i in self.incidents}):
            self.state_filter.addItem(st)
        self.state_filter.currentTextChanged.connect(self._apply_filters)
        tb.addWidget(self.state_filter)

        self.cat_buttons = {}
        for key, label in [
            ("Warehouse", "WAREHOUSE"),
            ("Arson", "ARSON"),
            ("Hazmat", "HAZMAT"),
            ("CSB", "CSB FEDERAL"),
            ("Industrial", "INDUSTRIAL")
        ]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setChecked(True)
            btn.toggled.connect(self._apply_filters)
            tb.addWidget(btn)
            self.cat_buttons[key] = btn

        self.rings_btn = QPushButton("5-MI PLUME")
        self.rings_btn.setCheckable(True)
        self.rings_btn.toggled.connect(self._apply_filters)
        tb.addWidget(self.rings_btn)

        self.sat_btn = QPushButton("SATELLITE")
        self.sat_btn.setCheckable(True)
        self.sat_btn.toggled.connect(self._toggle_basemap)
        tb.addWidget(self.sat_btn)

        self.sync_btn = QPushButton("↻ SYNC WIRE")
        self.sync_btn.clicked.connect(self._sync_live)
        tb.addWidget(self.sync_btn)

        self.export_btn = QPushButton("⬇ EXPORT")
        self.export_btn.clicked.connect(self._export_filtered)
        tb.addWidget(self.export_btn)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tb.addWidget(spacer)

        self.ts_label = QLabel()
        tb.addWidget(self.ts_label)

        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        dash = QFrame()
        dash.setObjectName("Dashboard")
        dash.setMaximumHeight(72)
        dash_layout = QHBoxLayout(dash)
        dash_layout.setContentsMargins(16, 8, 16, 8)
        dash_layout.setSpacing(12)

        for key, lbl_txt, css in [
            ("total", "MAPPED INCIDENTS", "DashValue"),
            ("warehouse", "WAREHOUSE / LOGISTICS", "DashOrange"),
            ("hazmat", "HAZMAT / CHEMICAL", "DashCyan"),
            ("csb", "CSB INVESTIGATIONS", "DashPurple"),
            ("arson", "ARSON / SUSPICIOUS", "DashPink"),
            ("news", "30-DAY LIVE WIRE", "DashCyan")
        ]:
            card = QFrame()
            card.setObjectName("KpiCard")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(8, 3, 8, 3)
            cl.setSpacing(0)
            lbl = QLabel(lbl_txt)
            lbl.setProperty("class", "DashLabel")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            val = QLabel("0")
            val.setProperty("class", css)
            val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(lbl)
            cl.addWidget(val)
            dash_layout.addWidget(card)
            self.kpi_labels[key] = val

        main_layout.addWidget(dash)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_tabs = QTabWidget()

        inc_tab = QWidget()
        inc_layout = QVBoxLayout(inc_tab)
        inc_layout.setContentsMargins(4, 4, 4, 4)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["FACILITY", "ST", "TYPE", "DIST"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._on_row_selected)
        inc_layout.addWidget(self.table, stretch=3)

        self.inspector = QTextEdit()
        self.inspector.setReadOnly(True)
        self.inspector.setPlaceholderText("Select any fire incident to inspect impact, source, and coordinates...")
        inc_layout.addWidget(self.inspector, stretch=1)
        left_tabs.addTab(inc_tab, "INCIDENTS")

        news_tab = QWidget()
        news_layout = QVBoxLayout(news_tab)
        news_layout.setContentsMargins(4, 4, 4, 4)
        self.news_table = QTableWidget(0, 3)
        self.news_table.setHorizontalHeaderLabels(["DATE", "HEADLINE (DOUBLE-CLICK TO OPEN)", "SOURCE"])
        self.news_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.news_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.news_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.news_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.news_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.news_table.cellDoubleClicked.connect(self._open_news_link)
        news_layout.addWidget(self.news_table)
        left_tabs.addTab(news_tab, "LIVE NEWS WIRE")

        self.webview = QWebEngineView()
        settings = self.webview.page().settings()
        settings.setAttribute(settings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(settings.WebAttribute.WebGLEnabled, True)
        settings.setAttribute(settings.WebAttribute.JavascriptEnabled, True)

        html_path = Path(__file__).resolve().parent / "fire_map.html"
        self.webview.setHtml(html_path.read_text(encoding="utf-8"), QUrl.fromLocalFile(str(html_path.parent) + "/"))
        self.webview.loadFinished.connect(self._on_map_loaded)

        splitter.addWidget(left_tabs)
        splitter.addWidget(self.webview)
        splitter.setSizes([430, 1250])
        main_layout.addWidget(splitter)

        self.status_lbl = QLabel("  SYSTEM: Ready  ")
        self.statusBar().addWidget(self.status_lbl)

        self._update_kpis()
        self._populate_table()

    def _on_map_loaded(self, ok):
        if ok:
            self.map_ready = True
            self._push_map()

    def _push_map(self):
        if self.map_ready:
            payload = json.dumps([i.to_dict() for i in self.incidents])
            self.webview.page().runJavaScript(f"if (typeof loadIncidents === 'function') loadIncidents({payload});")
            self._apply_filters()

    def _sync_live(self):
        self.sync_btn.setEnabled(False)
        self.sync_btn.setText("↻ SYNCING...")
        self.worker = NewsSyncWorker()
        self.worker.finished.connect(self._on_sync_done)
        self.worker.start()

    def _on_sync_done(self, articles, msg):
        self.sync_btn.setEnabled(True)
        self.sync_btn.setText("↻ SYNC WIRE")
        self.news_items = articles
        self.news_table.setRowCount(len(articles))
        for r, item in enumerate(articles):
            self.news_table.setItem(r, 0, QTableWidgetItem(item["date"]))
            self.news_table.setItem(r, 1, QTableWidgetItem(item["title"]))
            self.news_table.setItem(r, 2, QTableWidgetItem(item["source"]))
        self._push_map()
        self._update_proximity_bar(msg)

    def _update_proximity_bar(self, sync_msg=""):
        if self.incidents:
            closest = min(self.incidents, key=lambda x: x.distance_miles())
            self.status_lbl.setText(
                f"  ⚠ YOUR LOCATION PROXIMITY: Closest tracked fire is {closest.name} ({closest.city}, {closest.state}) at {closest.distance_miles()} mi  |  {sync_msg}  "
            )

    def _apply_filters(self):
        q = self.search.text().strip().lower()
        st = self.state_filter.currentText() or "ALL"
        cats = {k: btn.isChecked() for k, btn in self.cat_buttons.items()}
        rings = self.rings_btn.isChecked()

        self.filtered = []
        for i in self.incidents:
            if not cats.get(i.category, False):
                continue
            if st != "ALL" and i.state != st:
                continue
            if q:
                hay = f"{i.name} {i.city} {i.state} {i.category} {i.source} {i.note}".lower()
                if q not in hay:
                    continue
            self.filtered.append(i)

        self.filtered.sort(key=lambda x: x.distance_miles())
        self._populate_table()
        self._update_kpis()

        if self.map_ready:
            js = f"if (typeof applyFilters === 'function') applyFilters({json.dumps(q)}, {json.dumps(st)}, {json.dumps(cats)}, {str(rings).lower()});"
            self.webview.page().runJavaScript(js)

    def _populate_table(self):
        self.table.setRowCount(len(self.filtered))
        for r, i in enumerate(self.filtered):
            self.table.setItem(r, 0, QTableWidgetItem(i.name))
            self.table.setItem(r, 1, QTableWidgetItem(i.state))
            self.table.setItem(r, 2, QTableWidgetItem(i.category))
            self.table.setItem(r, 3, QTableWidgetItem(f"{i.distance_miles():.1f}"))

    def _on_row_selected(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        idx = rows[0].row()
        if idx < 0 or idx >= len(self.filtered):
            return
        i = self.filtered[idx]
        if self.map_ready:
            self.webview.page().runJavaScript(f"if (typeof flyToIncident === 'function') flyToIncident({json.dumps(i.id)});")
        self.inspector.setHtml(
            f"<b style='color:#ff6a00;font-size:13px;'>{i.name}</b><br>"
            f"<span style='color:#00e5ff;'>{i.category} &bull; {i.date} &bull; {i.source}</span><br><br>"
            f"<b>Location:</b> {i.city}, {i.state} ({i.lat:.4f}, {i.lng:.4f})<br>"
            f"<b>Distance from Your location:</b> {i.distance_miles():.1f} mi<br>"
            f"<b>Estimated Impact:</b> {i.damage}<br><br>"
            f"<span style='color:#ffea00;'>{i.note}</span>"
        )

    def _open_news_link(self, row, _col):
        if 0 <= row < len(self.news_items):
            link = self.news_items[row].get("link")
            if link:
                webbrowser.open(link)

    def _update_kpis(self):
        self.kpi_labels["total"].setText(str(len(self.filtered)))
        self.kpi_labels["warehouse"].setText(str(sum(1 for i in self.filtered if i.category == "Warehouse")))
        self.kpi_labels["hazmat"].setText(str(sum(1 for i in self.filtered if i.category == "Hazmat")))
        self.kpi_labels["csb"].setText(str(sum(1 for i in self.filtered if i.category == "CSB")))
        self.kpi_labels["arson"].setText(str(sum(1 for i in self.filtered if i.category == "Arson")))
        self.kpi_labels["news"].setText(str(len(self.news_items)))

    def _toggle_basemap(self, on):
        if self.map_ready:
            mode = "satellite" if on else "dark"
            self.webview.page().runJavaScript(f"if (typeof setBasemap === 'function') setBasemap({json.dumps(mode)});")

    def _export_filtered(self):
        path, selected = QFileDialog.getSaveFileName(
            self,
            "Export Filtered Fire Intel",
            str(Path.home() / "Desktop/warehouse_fire_intel_2026.csv"),
            "CSV File (*.csv);;GeoJSON File (*.geojson)"
        )
        if not path:
            return
        if path.endswith(".geojson") or "GeoJSON" in selected:
            features = [
                {"type": "Feature", "geometry": {"type": "Point", "coordinates": [i.lng, i.lat]}, "properties": i.to_dict()}
                for i in self.filtered
            ]
            with open(path, "w", encoding="utf-8") as fh:
                json.dump({"type": "FeatureCollection", "features": features}, fh, indent=2)
        else:
            fields = ["id", "name", "category", "date", "city", "state", "lat", "lng", "damage", "source", "distance_mi", "note"]
            with open(path, "w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=fields)
                writer.writeheader()
                for i in self.filtered:
                    row = i.to_dict()
                    writer.writerow({k: row.get(k, "") for k in fields})
        self.status_lbl.setText(f"  EXPORTED {len(self.filtered)} incidents to {Path(path).name}  ")

    def _tick_clock(self):
        self.ts_label.setText(datetime.now().strftime("%Y-%m-%d  %H:%M:%S  "))
        QTimer.singleShot(1000, self._tick_clock)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Punksm4ck Fire Command")
    win = FireCommandWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
