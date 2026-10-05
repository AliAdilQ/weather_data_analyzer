"""Capture actual rendered pages and verify desktop/mobile UI using Playwright.

Run against a seeded, running local application. Login defaults are local demo only.
"""

import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def capture(base_url, channel=None):
    output = ROOT / "screenshots"
    output.mkdir(exist_ok=True)
    errors = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=channel)
        page = browser.new_page(
            viewport={"width": 1440, "height": 900}, device_scale_factor=1
        )
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on(
            "response",
            lambda response: errors.append(f"{response.status}: {response.url}")
            if response.status >= 400 and response.url.startswith(base_url)
            else None,
        )

        def shot(path, name):
            page.goto(base_url + path, wait_until="networkidle")
            assert page.title() == "Weather Data Analyzer", (
                "Base URL is not this application"
            )
            page.screenshot(path=str(output / name), full_page=True)

        shot("/", "home.png")
        shot("/dashboard", "dashboard.png")
        assert page.locator("#temperature").evaluate(
            "(canvas) => !!Chart.getChart(canvas)"
        )
        page.goto(base_url, wait_until="networkidle")
        page.locator('input[name="city"]').fill("Yogyakarta")
        page.get_by_role("button", name="Explore weather").click()
        page.wait_for_url("**/weather/*")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(output / "weather-search.png"), full_page=True)
        shot("/compare?cities=Yogyakarta&cities=London", "compare-cities.png")
        page.goto(base_url + "/admin/login", wait_until="networkidle")
        page.get_by_label("Username").fill("admin")
        page.get_by_label("Password").fill("Admin123!")
        page.get_by_role("button", name="Sign in").click()
        page.wait_for_url(base_url + "/admin/")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(output / "admin-dashboard.png"), full_page=True)
        # Verify navigable internal anchors on all major pages, including admin.
        for path in (
            "/",
            "/dashboard",
            "/history",
            "/compare",
            "/about",
            "/admin/",
            "/admin/records",
            "/admin/searches",
            "/admin/users",
        ):
            page.goto(base_url + path, wait_until="networkidle")
            urls = page.locator("a[href]").evaluate_all(
                "(links) => links.map(a => a.href)"
            )
            for url in set(urls):
                if url.startswith(base_url):
                    response = page.request.get(url)
                    assert response.status < 400, f"Broken internal link: {url}"
        for width in (390, 768):
            page.set_viewport_size({"width": width, "height": 844})
            for path in ("/", "/dashboard", "/history", "/compare", "/admin/"):
                page.goto(base_url + path, wait_until="networkidle")
                assert page.evaluate(
                    "document.documentElement.scrollWidth <= window.innerWidth"
                ), f"Horizontal overflow: {path} at {width}px"
            if width == 390:
                page.goto(base_url, wait_until="networkidle")
                page.screenshot(path=str(output / "mobile-home.png"), full_page=True)
        browser.close()
    assert not errors, "\n".join(errors)
    print(
        "Five desktop screenshots and mobile preview captured. Charts, links, and responsive widths verified."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:5000")
    parser.add_argument(
        "--channel",
        default=None,
        help="Use chrome or msedge instead of bundled Chromium",
    )
    args = parser.parse_args()
    capture(args.base_url.rstrip("/"), args.channel)
