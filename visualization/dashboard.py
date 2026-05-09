"""
Dashboard Generator Module.
Creates a self-contained interactive HTML dashboard with insights,
charts, and map visualizations from the analysis results.
"""

import os
import json
import logging
from datetime import datetime
from collections import Counter
from config.settings import OUTPUT_DIR

logger = logging.getLogger(__name__)


class DashboardGenerator:
    """Generates an interactive HTML insights dashboard."""

    def __init__(self, output_dir=None):
        self.output_dir = output_dir or OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def generate(self, records, summary=None):
        """
        Generate a full HTML dashboard from analysis records.

        Args:
            records: List of analyzed article dicts.
            summary: Optional pre-computed summary dict.

        Returns:
            Path to generated HTML file.
        """
        if not summary:
            summary = self._compute_summary(records)

        html = self._build_html(records, summary)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.output_dir, f"dashboard_{ts}.html")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"📊 Dashboard saved: {filepath}")
        return filepath

    def _compute_summary(self, records):
        """Compute analysis summary statistics."""
        if not records:
            return {"total": 0}

        severity_counts = Counter(r.get("severity_level", "unknown") for r in records)
        sentiment_counts = Counter(r.get("sentiment_label", "neutral") for r in records)
        source_counts = Counter(r.get("source", "unknown") for r in records)

        all_keywords = []
        for r in records:
            kw = r.get("keywords_found", [])
            if isinstance(kw, str):
                kw = [k.strip() for k in kw.split(";")]
            all_keywords.extend(kw)
        keyword_counts = Counter(all_keywords).most_common(15)

        all_locations = []
        for r in records:
            locs = r.get("locations", [])
            if isinstance(locs, str):
                locs = [l.strip() for l in locs.split(";")]
            all_locations.extend([l for l in locs if l])
        location_counts = Counter(all_locations).most_common(15)

        sentiments = [r.get("sentiment_compound", 0) for r in records if r.get("sentiment_compound") is not None]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0

        casualties = [r.get("casualty_count", 0) for r in records if r.get("casualty_count")]
        total_casualties = sum(casualties)

        return {
            "total": len(records),
            "severity": dict(severity_counts),
            "sentiment": dict(sentiment_counts),
            "sources": dict(source_counts),
            "top_keywords": keyword_counts,
            "top_locations": location_counts,
            "avg_sentiment": round(avg_sentiment, 3),
            "total_casualties": total_casualties,
            "date_range": self._get_date_range(records),
        }

    def _get_date_range(self, records):
        dates = [r.get("date") for r in records if r.get("date") and r.get("date") != "Unknown"]
        if not dates:
            return {"start": "N/A", "end": "N/A"}
        dates.sort()
        return {"start": dates[0], "end": dates[-1]}

    def _build_html(self, records, summary):
        """Build the complete HTML dashboard."""
        severity_data = json.dumps(summary.get("severity", {}))
        sentiment_data = json.dumps(summary.get("sentiment", {}))
        source_data = json.dumps(summary.get("sources", {}))
        keyword_data = json.dumps(summary.get("top_keywords", []))
        location_data = json.dumps(summary.get("top_locations", []))

        # Build map markers from records with coordinates
        markers = []
        for r in records:
            lat = r.get("latitude") or r.get("lat")
            lon = r.get("longitude") or r.get("lon")
            if lat and lon:
                try:
                    markers.append({
                        "lat": float(lat), "lon": float(lon),
                        "title": r.get("title", "")[:80],
                        "severity": r.get("severity_level", "unknown"),
                        "url": r.get("url", ""),
                    })
                except (ValueError, TypeError):
                    pass
        markers_json = json.dumps(markers)

        # Build articles table
        table_rows = ""
        for r in records:
            sev = r.get("severity_level", "unknown")
            sev_class = {"fatal": "sev-fatal", "severe": "sev-severe", "moderate": "sev-moderate", "minor": "sev-minor"}.get(sev, "sev-unknown")
            sent = r.get("sentiment_label", "neutral")
            title = r.get("title", "N/A")[:60]
            url = r.get("url", "#")
            date = r.get("date", "N/A")
            source = r.get("source", "N/A")
            cas = r.get("casualty_count", 0)
            score = r.get("sentiment_compound", 0)
            locs = r.get("locations", "")
            if isinstance(locs, list):
                locs = ", ".join(locs)

            table_rows += f"""<tr>
                <td><a href="{url}" target="_blank">{title}</a></td>
                <td>{date}</td><td>{source}</td>
                <td><span class="badge {sev_class}">{sev.upper()}</span></td>
                <td>{sent}</td><td>{score:.2f}</td><td>{cas}</td>
                <td>{locs[:40]}</td></tr>"""

        return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Road Safety NLP Analysis Dashboard - Hyderabad</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9/dist/leaflet.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',system-ui,-apple-system,sans-serif;background:#0f172a;color:#e2e8f0;line-height:1.6}}
.header{{background:linear-gradient(135deg,#1e293b 0%,#0f172a 100%);border-bottom:1px solid #334155;padding:24px 40px}}
.header h1{{font-size:28px;background:linear-gradient(90deg,#38bdf8,#818cf8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800}}
.header p{{color:#94a3b8;margin-top:4px}}
.container{{max-width:1400px;margin:0 auto;padding:24px}}
.stats-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:24px}}
.stat-card{{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:20px;text-align:center}}
.stat-card .value{{font-size:36px;font-weight:800;background:linear-gradient(135deg,#38bdf8,#818cf8);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.stat-card .label{{color:#94a3b8;font-size:13px;margin-top:4px}}
.charts-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:20px;margin-bottom:24px}}
.chart-card{{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:20px}}
.chart-card h3{{color:#f1f5f9;margin-bottom:12px;font-size:16px}}
#map{{height:400px;border-radius:8px;margin-bottom:24px}}
.map-card{{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:20px;margin-bottom:24px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th{{background:#334155;color:#f1f5f9;padding:10px 12px;text-align:left;position:sticky;top:0}}
td{{padding:8px 12px;border-bottom:1px solid #1e293b}}
tr:hover{{background:#1e293b}}
a{{color:#38bdf8;text-decoration:none}}a:hover{{text-decoration:underline}}
.badge{{padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}}
.sev-fatal{{background:#dc2626;color:#fff}}.sev-severe{{background:#ea580c;color:#fff}}
.sev-moderate{{background:#ca8a04;color:#fff}}.sev-minor{{background:#16a34a;color:#fff}}
.sev-unknown{{background:#475569;color:#fff}}
.table-card{{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:20px;overflow-x:auto;max-height:500px;overflow-y:auto}}
.table-card h3{{margin-bottom:12px;color:#f1f5f9}}
</style></head><body>
<div class="header">
<h1>🚦 Road Safety NLP Analysis Dashboard</h1>
<p>Hyderabad Region — {summary.get('date_range',{}).get('start','N/A')} to {summary.get('date_range',{}).get('end','N/A')} — Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
</div>
<div class="container">
<div class="stats-grid">
<div class="stat-card"><div class="value">{summary.get('total',0)}</div><div class="label">Articles Analyzed</div></div>
<div class="stat-card"><div class="value">{summary.get('severity',{}).get('fatal',0)}</div><div class="label">Fatal Incidents</div></div>
<div class="stat-card"><div class="value">{summary.get('total_casualties',0)}</div><div class="label">Total Casualties</div></div>
<div class="stat-card"><div class="value">{summary.get('avg_sentiment',0):.2f}</div><div class="label">Avg Sentiment Score</div></div>
<div class="stat-card"><div class="value">{len(summary.get('sources',{}))}</div><div class="label">News Sources</div></div>
</div>
<div class="charts-grid">
<div class="chart-card"><h3>Severity Distribution</h3><canvas id="severityChart"></canvas></div>
<div class="chart-card"><h3>Sentiment Distribution</h3><canvas id="sentimentChart"></canvas></div>
<div class="chart-card"><h3>Top Keywords</h3><canvas id="keywordsChart"></canvas></div>
<div class="chart-card"><h3>Articles by Source</h3><canvas id="sourcesChart"></canvas></div>
</div>
<div class="map-card"><h3 style="color:#f1f5f9;margin-bottom:12px">📍 Incident Locations</h3><div id="map"></div></div>
<div class="table-card"><h3>📋 All Analyzed Articles</h3>
<table><thead><tr><th>Title</th><th>Date</th><th>Source</th><th>Severity</th><th>Sentiment</th><th>Score</th><th>Casualties</th><th>Locations</th></tr></thead>
<tbody>{table_rows}</tbody></table></div>
</div>
<script>
const sevColors={{"fatal":"#dc2626","severe":"#ea580c","moderate":"#ca8a04","minor":"#16a34a","unclassified":"#475569","unknown":"#475569"}};
const sentColors={{"negative":"#dc2626","neutral":"#ca8a04","positive":"#16a34a"}};
function makeChart(id,type,labels,data,colors){{
  new Chart(document.getElementById(id),{{type,data:{{labels,datasets:[{{data,backgroundColor:colors,borderWidth:0}}]}},
    options:{{responsive:true,plugins:{{legend:{{labels:{{color:'#e2e8f0'}}}}}},scales:type==='bar'?{{y:{{ticks:{{color:'#94a3b8'}}}},x:{{ticks:{{color:'#94a3b8'}}}}}}:undefined}}}});
}}
const sev={severity_data};const sent={sentiment_data};
makeChart('severityChart','doughnut',Object.keys(sev),Object.values(sev),Object.keys(sev).map(k=>sevColors[k]||'#475569'));
makeChart('sentimentChart','doughnut',Object.keys(sent),Object.values(sent),Object.keys(sent).map(k=>sentColors[k]||'#475569'));
const kwData={keyword_data};
makeChart('keywordsChart','bar',kwData.map(k=>k[0]),kwData.map(k=>k[1]),kwData.map(()=>'#38bdf8'));
const srcData={source_data};
makeChart('sourcesChart','bar',Object.keys(srcData),Object.values(srcData),Object.keys(srcData).map(()=>'#818cf8'));
// Map
const map=L.map('map').setView([17.385,78.4867],11);
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png',{{maxZoom:19}}).addTo(map);
const markers={markers_json};
markers.forEach(m=>{{
  const color=sevColors[m.severity]||'#475569';
  const icon=L.divIcon({{html:`<div style="background:${{color}};width:12px;height:12px;border-radius:50%;border:2px solid #fff"></div>`,className:'',iconSize:[16,16]}});
  L.marker([m.lat,m.lon],{{icon}}).addTo(map).bindPopup(`<b>${{m.title}}</b><br>Severity: ${{m.severity}}<br><a href="${{m.url}}" target="_blank">Read</a>`);
}});
</script></body></html>"""
