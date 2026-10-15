from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import helpful_content_lint as hcl


def test_clean_expert_content_scores_high() -> None:
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Database Performance Optimization Guide (2026)</title>
    </head>
    <body>
        <h1>PostgreSQL 16 Indexing Benchmarks</h1>
        <div class="byline">By Alex Mercer, Principal Database Engineer</div>
        <p>In our experiment, our team tested B-tree vs BRIN indexing across 50,000,000 rows. We measured p99 query latency dropping from 420ms to 85ms (79.7% reduction).</p>
        <p>According to research from PostgreSQL Global Development Group, proper fillfactor settings reduce table bloat.</p>
        <table>
            <tr><th>Index Type</th><th>Build Time</th><th>Query Latency</th></tr>
            <tr><td>B-Tree</td><td>142s</td><td>12ms</td></tr>
            <tr><td>BRIN</td><td>18s</td><td>45ms</td></tr>
        </table>
    </body>
    </html>
    """
    result = hcl.scan_content(html)
    assert result["total_score"] >= 75
    assert len(result["signals"]["slop_samples"]) == 0
    assert len(result["signals"]["clickbait_flags"]) == 0
    assert result["signals"]["has_author"] is True
    assert result["signals"]["has_experience"] is True
    assert result["signals"]["has_sources"] is True
    assert result["signals"]["has_tables"] is True


def test_ai_slop_and_clickbait_flagged() -> None:
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>This One Weird Trick Will Blow Your Mind</title>
    </head>
    <body>
        <h1>Shocking Truth About Modern Marketing</h1>
        <p>In the fast-paced world of today's digital landscape, we delve into the tapestry of modern SEO.</p>
        <p>It is crucial to remember that this serves as a testament to the power of AI. Look no further for a game-changer.</p>
        <p>Without further ado, let us look at generic marketing tips.</p>
    </body>
    </html>
    """
    result = hcl.scan_content(html)
    assert result["signals"]["slop_count"] >= 3
    assert len(result["signals"]["clickbait_flags"]) >= 1
    assert result["total_score"] < 70
    assert result["grade"] in ("C", "D", "F")


def test_missing_byline_and_evidence_lowers_score() -> None:
    html = """
    <html>
    <body>
        <h1>Simple Blog Post</h1>
        <p>Here are some thoughts about cooking pasta. Pasta is good. It comes in different shapes.</p>
    </body>
    </html>
    """
    result = hcl.scan_content(html)
    assert result["signals"]["has_author"] is False
    assert result["signals"]["has_sources"] is False
    assert result["signals"]["has_experience"] is False
