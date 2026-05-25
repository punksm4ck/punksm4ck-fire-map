import tkinter as tk
from tkinter import ttk, messagebox
import tkintermapview
import urllib.request
import xml.etree.ElementTree as ET
import webbrowser
from datetime import datetime
import threading
import json
import os
import geocoder
import re
from collections import Counter

class AegisOmniTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Aegis Intelligence: US Industrial Fire Omni-Tracker")
        self.root.geometry("1600x900")
        self.root.configure(bg="#121212")
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aegis_omni_db.json")
        self.db = {"markers": [], "news": []}
        self.feed_visible = False
        self.init_ui()
        self.recover_database()
        self.trigger_update_cycle()

    def init_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1e1e1e", foreground="#ffffff", fieldbackground="#1e1e1e", rowheight=30, font=("Segoe UI", 10))
        style.map("Treeview", background=[("selected", "#005a9e")])
        style.configure("Treeview.Heading", background="#2d2d30", foreground="#ffffff", font=("Segoe UI", 11, "bold"))
        style.configure("TButton", padding=8, relief="flat", background="#333333", foreground="#ffffff", font=("Segoe UI", 10, "bold"))
        style.map("TButton", background=[("active", "#454545")])
        style.configure("Stat.TLabel", background="#1a1a1a", foreground="#00a8ff", font=("Segoe UI", 14, "bold"))
        style.configure("StatTitle.TLabel", background="#1a1a1a", foreground="#a0a0a0", font=("Segoe UI", 10))

        header_frame = tk.Frame(self.root, bg="#121212")
        header_frame.pack(fill="x", padx=15, pady=10)

        title_label = tk.Label(header_frame, text="AEGIS OMNI-TRACKER: US Industrial Fires (Post April 6, 2026)", font=("Segoe UI", 18, "bold"), bg="#121212", fg="#00a8ff")
        title_label.pack(side="left")

        btn_frame = tk.Frame(header_frame, bg="#121212")
        btn_frame.pack(side="right")

        self.toggle_feed_btn = ttk.Button(btn_frame, text="Show Intelligence Feed", command=self.toggle_feed)
        self.toggle_feed_btn.pack(side="left", padx=5)

        refresh_btn = ttk.Button(btn_frame, text="Force Omni-Sync", command=self.trigger_update_cycle)
        refresh_btn.pack(side="left", padx=5)

        self.main_container = tk.Frame(self.root, bg="#121212")
        self.main_container.pack(fill="both", expand=True, padx=15, pady=5)

        self.map_frame = tk.Frame(self.main_container, bg="#121212")
        self.map_frame.pack(side="left", fill="both", expand=True)

        self.map_widget = tkintermapview.TkinterMapView(self.map_frame, corner_radius=0)
        self.map_widget.pack(fill="both", expand=True)
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.map_widget.set_position(39.8283, -98.5795)
        self.map_widget.set_zoom(4)

        self.right_panel = tk.Frame(self.main_container, bg="#1a1a1a", width=350)
        self.right_panel.pack(side="right", fill="y", padx=(10, 0))
        self.right_panel.pack_propagate(False)

        stats_header = tk.Label(self.right_panel, text="HEURISTIC ANALYSIS", font=("Segoe UI", 12, "bold"), bg="#2d2d30", fg="#ffffff", pady=10)
        stats_header.pack(fill="x")

        self.stat_vars = {
            "total_incidents": tk.StringVar(value="0"),
            "states_affected": tk.StringVar(value="0"),
            "arson_suspected": tk.StringVar(value="0"),
            "total_reports": tk.StringVar(value="0"),
            "primary_hotspot": tk.StringVar(value="N/A")
        }

        self.build_stat_widget("Total Confirmed Incidents", self.stat_vars["total_incidents"])
        self.build_stat_widget("States Affected", self.stat_vars["states_affected"])
        self.build_stat_widget("Suspected Arson / Intentional", self.stat_vars["arson_suspected"])
        self.build_stat_widget("Intelligence Reports Scraped", self.stat_vars["total_reports"])
        self.build_stat_widget("Primary Hotspot Zone", self.stat_vars["primary_hotspot"])

        self.news_frame = tk.Frame(self.right_panel, bg="#1a1a1a")
        news_header = tk.Label(self.news_frame, text="LIVE INTEL FEED", font=("Segoe UI", 10, "bold"), bg="#2d2d30", fg="#ffffff", pady=5)
        news_header.pack(fill="x", pady=(15, 0))

        columns = ("pub_date", "headline")
        self.data_view = ttk.Treeview(self.news_frame, columns=columns, show="headings", style="Treeview", displaycolumns=("headline",))
        self.data_view.heading("headline", text="Recent Reports")
        self.data_view.column("headline", width=330, anchor="w")
        self.data_view.bind("<Double-1>", self.launch_source_url)

        self.context_menu = tk.Menu(self.root, tearoff=0, bg="#2d2d30", fg="#ffffff", activebackground="#005a9e")
        self.context_menu.add_command(label="Open Intel Link", command=self.launch_from_menu)
        self.data_view.bind("<Button-3>", self.popup_menu)

        self.sys_status = tk.StringVar()
        self.sys_status.set("Aegis Omni-Subsystem Initializing...")
        status_banner = tk.Label(self.root, textvariable=self.sys_status, bg="#005a9e", fg="#ffffff", anchor="w", font=("Segoe UI", 10, "bold"), padx=10, pady=5)
        status_banner.pack(fill="x", side="bottom")

    def build_stat_widget(self, title, var):
        container = tk.Frame(self.right_panel, bg="#1a1a1a", pady=10)
        container.pack(fill="x", padx=15)
        ttk.Label(container, text=title, style="StatTitle.TLabel").pack(anchor="w")
        ttk.Label(container, textvariable=var, style="Stat.TLabel").pack(anchor="w")
        tk.Frame(container, bg="#333333", height=1).pack(fill="x", pady=(5, 0))

    def toggle_feed(self):
        if self.feed_visible:
            self.data_view.pack_forget()
            self.news_frame.pack_forget()
            self.toggle_feed_btn.config(text="Show Intelligence Feed")
            self.feed_visible = False
        else:
            self.news_frame.pack(fill="both", expand=True)
            self.data_view.pack(fill="both", expand=True)
            self.toggle_feed_btn.config(text="Hide Intelligence Feed")
            self.feed_visible = True

    def popup_menu(self, event):
        item = self.data_view.identify_row(event.y)
        if item:
            self.data_view.selection_set(item)
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def launch_from_menu(self):
        selected = self.data_view.selection()
        if selected:
            url_tag = self.data_view.item(selected[0], "tags")
            if url_tag:
                webbrowser.open(url_tag[0])

    def launch_source_url(self, event):
        self.launch_from_menu()

    def recover_database(self):
        default_markers = [
            {"city": "Ontario, CA", "lat": 34.0633, "lon": -117.6509, "desc": "Kimberly-Clark Warehouse (Arson)"},
            {"city": "Newark, NJ", "lat": 40.7357, "lon": -74.1724, "desc": "Lister Ave Warehouse Complex"},
            {"city": "West Jefferson, OH", "lat": 39.9442, "lon": -83.2691, "desc": "Amazon Warehouse (Solar Panel Fire)"},
            {"city": "Queens, NY", "lat": 40.7834, "lon": -73.8464, "desc": "College Point Lumberyard/Warehouse"},
            {"city": "Bakersfield, CA", "lat": 35.3733, "lon": -119.0187, "desc": "Abandoned Warehouse near Recycling Center"},
            {"city": "East Providence, RI", "lat": 41.8137, "lon": -71.3701, "desc": "Aspen Aerogels Plant"},
            {"city": "Bedford Park, IL", "lat": 41.7611, "lon": -87.8017, "desc": "Ingredion Food Processing Plant"},
            {"city": "Wayne County, OH", "lat": 40.8300, "lon": -81.9332, "desc": "Southwood Lumber Pallet Factory"},
            {"city": "Bethlehem, PA", "lat": 40.6259, "lon": -75.3705, "desc": "Commercial Trash Station"},
            {"city": "Gwinnett County, GA", "lat": 33.9526, "lon": -84.0203, "desc": "Commercial Trash Station"},
            {"city": "Detroit, MI", "lat": 42.3314, "lon": -83.0458, "desc": "Aevitas Specialty Services (Recycling)"},
            {"city": "Abington Township, PA", "lat": 40.1215, "lon": -75.1196, "desc": "SPS Technologies Factory Fire"},
            {"city": "Miami-Dade County, FL", "lat": 25.7617, "lon": -80.1918, "desc": "Industrial Fire (Miami-Dade County)"},
        ]

        if not os.path.exists(self.db_path):
            self.db["markers"] = default_markers
            self.secure_database()
        else:
            try:
                with open(self.db_path, "r") as f:
                    self.db = json.load(f)

                for dm in default_markers:
                    if not any(existing.get("city") == dm["city"] for existing in self.db.get("markers", [])):
                        self.db.setdefault("markers", []).append(dm)
                self.secure_database()
            except Exception:
                pass
        self.render_map()
        self.render_news()
        self.update_heuristics()

    def secure_database(self):
        try:
            with open(self.db_path, "w") as f:
                json.dump(self.db, f)
        except Exception:
            pass

    def render_map(self):
        self.map_widget.delete_all_marker()
        for incident in self.db.get("markers", []):
            self.map_widget.set_marker(incident["lat"], incident["lon"], text=f"{incident['city']}\n{incident['desc']}")

    def render_news(self):
        for entry in self.data_view.get_children():
            self.data_view.delete(entry)
        for item in self.db.get("news", []):
            formatted_date = " ".join(item["date"].split(" ")[:5])
            self.data_view.insert("", "end", values=(formatted_date, item["title"], item["source"]), tags=(item["link"],))

    def update_heuristics(self):
        markers = self.db.get("markers", [])
        news = self.db.get("news", [])

        total_incidents = len(markers)
        self.stat_vars["total_incidents"].set(str(total_incidents))

        states = []
        for m in markers:
            parts = m.get("city", "").split(",")
            if len(parts) > 1:
                states.append(parts[-1].strip())

        unique_states = len(set(states))
        self.stat_vars["states_affected"].set(str(unique_states))

        if states:
            most_common_state = Counter(states).most_common(1)[0][0]
            self.stat_vars["primary_hotspot"].set(most_common_state)

        arson_count = sum(1 for m in markers if "arson" in m.get("desc", "").lower())
        for n in news:
            if "arson" in n.get("title", "").lower() and not any("arson" in m.get("desc", "").lower() for m in markers):
                pass

        self.stat_vars["arson_suspected"].set(f"{arson_count} Verified")
        self.stat_vars["total_reports"].set(str(len(news)))

    def trigger_update_cycle(self):
        self.sys_status.set("Establishing uplink to global news feeds and executing heuristic analysis...")
        threading.Thread(target=self.execute_omni_pull, daemon=True).start()

    def execute_omni_pull(self):
        try:
            target_url = "https://news.google.com/rss/search?q=warehouse+fire+USA+after:2026-04-05&hl=en-US&gl=US&ceid=US:en"
            headers = {'User-Agent': 'Mozilla/5.0'}
            request_obj = urllib.request.Request(target_url, headers=headers)
            with urllib.request.urlopen(request_obj, timeout=15) as network_response:
                raw_xml = network_response.read()

            xml_tree = ET.fromstring(raw_xml)
            new_items_found = 0

            for node in xml_tree.findall(".//item"):
                title = node.find("title").text if node.find("title") is not None else "Unknown Incident"
                link = node.find("link").text if node.find("link") is not None else ""
                date = node.find("pubDate").text if node.find("pubDate") is not None else "Unknown Time"
                source = node.find("source").text if node.find("source") is not None else "Unverified Source"

                if not any(existing.get("link") == link for existing in self.db.get("news", [])):
                    self.db.setdefault("news", []).append({"title": title, "link": link, "date": date, "source": source})
                    new_items_found += 1
                    self.extract_and_geocode(title)

            self.db["news"].sort(key=lambda x: x.get("date", ""), reverse=True)
            self.secure_database()
            self.root.after(0, self.render_news)
            self.root.after(0, self.render_map)
            self.root.after(0, self.update_heuristics)

            current_time = datetime.now().strftime('%H:%M:%S on %Y-%m-%d')
            self.root.after(0, lambda: self.sys_status.set(f"Omni-Sync complete at {current_time}. Tracking {len(self.db.get('markers', []))} incidents. Next sweep in 15 minutes."))
        except Exception:
            self.root.after(0, lambda: self.sys_status.set("Uplink failure. Operating on local cache. Next sweep attempting in 15 minutes."))

        self.root.after(900000, self.trigger_update_cycle)

    def extract_and_geocode(self, title):
        match = re.search(r"([A-Z][a-zA-Z\s\-]+(?:\s*County)?,\s(?:[A-Z]{2}|[A-Z][a-z]+))", title)
        if match:
            location_str = match.group(1).strip()
            if not any(existing.get("city") == location_str for existing in self.db.get("markers", [])):
                try:
                    g = geocoder.osm(location_str)
                    if g.ok and g.lat and g.lng:
                        self.db["markers"].append({"city": location_str, "lat": g.lat, "lon": g.lng, "desc": "Dynamically Tracked via Live Feed"})
                except Exception:
                    pass

if __name__ == "__main__":
    main_window = tk.Tk()
    app = AegisOmniTracker(main_window)
    main_window.mainloop()
