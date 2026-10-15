from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import rendering_gap_lint as rgl


def test_identical_raw_and_rendered_passes() -> None:
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Server Rendered Page</title>
        <link rel="canonical" href="https://example.com/page">
        <script type="application/ld+json">{"@context": "https://schema.org", "@type": "Article", "headline": "Test"}</script>
    </head>
    <body>
        <h1>Primary Heading</h1>
        <p>Full content rendered by the server.</p>
        <a href="/about">About Us</a>
        <a href="/pricing">Pricing</a>
    </body>
    </html>
    """
    result = rgl.compare_raw_vs_rendered(html, html)
    assert result["score"] == 100
    assert result["rendering_risk"] == "LOW"
    assert result["raw_metrics"]["links"] == 3
    assert result["rendered_metrics"]["links"] == 3


def test_discrepancy_detected_when_dom_hydrates_content() -> None:
    raw_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>App Shell</title>
    </head>
    <body>
        <div id="root">Loading...</div>
    </body>
    </html>
    """

    rendered_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>App Loaded</title>
        <link rel="canonical" href="https://example.com/app">
        <script type="application/ld+json">{"@context": "https://schema.org", "@type": "WebApplication", "name": "App"}</script>
    </head>
    <body>
        <div id="root">
            <h1>Application Dashboard</h1>
            <nav>
                <a href="/dashboard">Dashboard</a>
                <a href="/settings">Settings</a>
                <a href="/logout">Logout</a>
            </nav>
        </div>
    </body>
    </html>
    """

    result = rgl.compare_raw_vs_rendered(raw_html, rendered_html)
    assert result["score"] < 70
    assert result["rendering_risk"] in ("CRITICAL", "HIGH")
    assert result["discrepancies"]["links_missing_in_raw_count"] == 4
    assert result["discrepancies"]["schema_missing_in_raw_count"] >= 1
