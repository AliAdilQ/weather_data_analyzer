# Screenshot generation

These screenshots show real rendered pages with seeded synthetic data. Regenerate them after UI changes:

```bash
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python seed.py
python run.py
```

In a second terminal, with the virtual environment activated:

```bash
python scripts/capture_screenshots.py
```

The script uses a 1440×900 desktop viewport, captures full pages, signs into the local demo admin account, verifies internal links and rendered charts, and checks layout overflow at 390px and 768px. It also saves `mobile-home.png`. To use installed Edge instead: `python scripts/capture_screenshots.py --channel msedge`.

Every execution adds one real search to the local demonstration database. Never point this script at a public production deployment with demo credentials.
