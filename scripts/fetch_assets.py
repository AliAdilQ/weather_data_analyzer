"""Refresh pinned, locally served frontend dependencies and licenses."""

from pathlib import Path
from urllib.request import urlretrieve

ROOT = Path(__file__).resolve().parents[1] / "app/static/vendor"
ASSETS = {
    "bootstrap.min.css": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css",
    "bootstrap.bundle.min.js": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js",
    "bootstrap-icons.css": "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.css",
    "fonts/bootstrap-icons.woff2": "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/fonts/bootstrap-icons.woff2",
    "fonts/bootstrap-icons.woff": "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/fonts/bootstrap-icons.woff",
    "chart.umd.js": "https://cdn.jsdelivr.net/npm/chart.js@4.5.0/dist/chart.umd.js",
    "bootstrap.LICENSE": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/LICENSE",
    "bootstrap-icons.LICENSE": "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/LICENSE",
    "chartjs.LICENSE": "https://cdn.jsdelivr.net/npm/chart.js@4.5.0/LICENSE.md",
}

if __name__ == "__main__":
    for name, url in ASSETS.items():
        target = ROOT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        urlretrieve(url, target)
        print(name)
