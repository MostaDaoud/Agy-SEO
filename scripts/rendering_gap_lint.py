#!/usr/bin/env python3
"""
Visual Semantics & Rendering Gap Detector.

Audits discrepancy between Raw Server HTML and Rendered DOM HTML (Koray Tugberk
Gubur & Kunjal Chawhan framework). Identifies content, links, headings, and schema
hidden behind client-side JavaScript hydration that AI search crawlers with strict
rendering budgets fail to ingest.

Usage:
    python scripts/rendering_gap_lint.py https://example.com
    python scripts/rendering_gap_lint.py --raw raw.html --rendered rendered.html
    python scripts/rendering_gap_lint.py --raw raw.html --rendered rendered.html --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Set

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from url_safety import URLSafetyError, decode_response_text, safe_requests_get


def _extract_dom_metrics(html: str) -> Dict[str, Any]:
    """Extract words, links, headings, and schema elements from HTML."""
    clean = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", "", html, flags=re.S | re.I)

    # Word extraction
    text = re.sub(r"<[^>]+>", " ", clean)
    words = [w for w in re.split(r"\s+", text) if w]

    # Links extraction
    hrefs = set(re.findall(r'href=["\'](https?://[^"\']+|/[^"\']*)["\']', clean, re.I))

    # Headings extraction
    h1s = [re.sub(r"<[^>]+>", "", h).strip() for h in re.findall(r"<h1[^>]*>(.*?)</h1>", clean, re.I | re.S)]
    h2s = [re.sub(r"<[^>]+>", "", h).strip() for h in re.findall(r"<h2[^>]*>(.*?)</h2>", clean, re.I | re.S)]

    # Schema blocks
    schema_blocks = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.I | re.S)

    return {
        "word_count": len(words),
        "link_count": len(hrefs),
        "links": hrefs,
        "h1s": h1s,
        "h2s": h2s,
        "schema_count": len(schema_blocks),
    }


def compare_raw_vs_rendered(raw_html: str, rendered_html: str) -> Dict[str, Any]:
    """Compare Raw HTML against Rendered HTML and report discrepancies."""
    raw = _extract_dom_metrics(raw_html)
    ren = _extract_dom_metrics(rendered_html)

    word_diff = ren["word_count"] - raw["word_count"]
    word_growth_pct = round((word_diff / max(1, raw["word_count"])) * 100, 1)

    links_missing_in_raw = sorted(list(ren["links"] - raw["links"]))
    h1_missing_in_raw = [h for h in ren["h1s"] if h not in raw["h1s"]]
    h2_missing_in_raw = [h for h in ren["h2s"] if h not in raw["h2s"]]
    schema_missing_in_raw = ren["schema_count"] - raw["schema_count"]

    findings = []
    risk_level = "LOW"

    # High rendering risk: >40% of words added client-side
    if word_growth_pct >= 40.0:
        risk_level = "HIGH"
        findings.append({
            "type": "WORD_COUNT_GAP",
            "severity": "CRITICAL",
            "detail": f"{word_growth_pct}% of text content is generated via client-side JavaScript ({raw['word_count']} raw words vs {ren['word_count']} rendered words). AI crawlers may index thin content.",
        })
    elif word_growth_pct >= 20.0:
        if risk_level != "HIGH":
            risk_level = "MEDIUM"
        findings.append({
            "type": "WORD_COUNT_GAP",
            "severity": "WARNING",
            "detail": f"{word_growth_pct}% text expansion client-side ({raw['word_count']} raw vs {ren['word_count']} rendered words).",
        })

    # Missing links in raw HTML
    if len(links_missing_in_raw) >= 5:
        risk_level = "HIGH"
        findings.append({
            "type": "LINKS_HIDDEN_BEHIND_JS",
            "severity": "CRITICAL",
            "detail": f"{len(links_missing_in_raw)} links are hidden behind client-side execution and absent from server HTML. Crawl budget and link equity are impaired.",
            "samples": links_missing_in_raw[:5],
        })
    elif links_missing_in_raw:
        findings.append({
            "type": "LINKS_HIDDEN_BEHIND_JS",
            "severity": "WARNING",
            "detail": f"{len(links_missing_in_raw)} links appear only in rendered DOM.",
            "samples": links_missing_in_raw[:3],
        })

    # Heading hierarchy missing in raw
    if h1_missing_in_raw:
        findings.append({
            "type": "H1_INJECTED_VIA_JS",
            "severity": "CRITICAL",
            "detail": f"H1 headline ({h1_missing_in_raw[0] if h1_missing_in_raw else ''}) is absent from server HTML and injected client-side.",
        })
    if len(h2_missing_in_raw) >= 2:
        findings.append({
            "type": "H2_HEADINGS_INJECTED_VIA_JS",
            "severity": "WARNING",
            "detail": f"{len(h2_missing_in_raw)} H2 section headings require client-side execution to be visible to search engines.",
        })

    # Schema missing in raw
    if schema_missing_in_raw > 0:
        findings.append({
            "type": "SCHEMA_INJECTED_CLIENT_SIDE",
            "severity": "HIGH",
            "detail": f"{schema_missing_in_raw} JSON-LD structured data block(s) are injected client-side after DOMContentLoaded.",
        })

    score = 100
    for f in findings:
        if f["severity"] == "CRITICAL":
            score -= 25
        elif f["severity"] == "HIGH":
            score -= 15
        elif f["severity"] == "WARNING":
            score -= 8

    return {
        "score": max(0, score),
        "rendering_risk": risk_level,
        "raw_metrics": {
            "words": raw["word_count"],
            "links": raw["link_count"],
            "h1s": raw["h1s"],
            "h2_count": len(raw["h2s"]),
            "schema_blocks": raw["schema_count"],
        },
        "rendered_metrics": {
            "words": ren["word_count"],
            "links": ren["link_count"],
            "h1s": ren["h1s"],
            "h2_count": len(ren["h2s"]),
            "schema_blocks": ren["schema_count"],
        },
        "discrepancies": {
            "word_count_delta": word_diff,
            "word_growth_pct": word_growth_pct,
            "links_missing_in_raw_count": len(links_missing_in_raw),
            "h1_missing_in_raw": h1_missing_in_raw,
            "h2_missing_in_raw_count": len(h2_missing_in_raw),
            "schema_missing_in_raw_count": schema_missing_in_raw,
        },
        "findings": findings,
    }


def audit_single_raw_html(html: str) -> Dict[str, Any]:
    """Analyze raw server HTML for indicators of JavaScript rendering vulnerability."""
    metrics = _extract_dom_metrics(html)

    # Empty SPA root detection
    empty_spa_roots = re.findall(
        r'<div[^>]*(id|class)=["\'](root|__next|app|app-root)["\'][^>]*>\s*</div>',
        html,
        re.I
    )

    # Heavy script bundle footprint
    scripts = re.findall(r'<script\b[^>]*src=["\']([^"\']+)["\']', html, re.I)

    has_client_side_vulnerability = bool(empty_spa_roots or metrics["word_count"] < 250 and len(scripts) >= 3)

    return {
        "mode": "heuristic_single_pass",
        "word_count": metrics["word_count"],
        "link_count": metrics["link_count"],
        "h1s": metrics["h1s"],
        "h2_count": len(metrics["h2s"]),
        "schema_blocks": metrics["schema_count"],
        "empty_spa_root_detected": bool(empty_spa_roots),
        "script_tags_count": len(scripts),
        "client_side_vulnerability_detected": has_client_side_vulnerability,
        "recommendation": (
            "Potential client-side rendering vulnerability detected. Provide --rendered HTML to measure exact DOM gap."
            if has_client_side_vulnerability
            else "Server HTML contains substantial crawlable content."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit rendering discrepancies between Raw Server HTML and Rendered DOM HTML."
    )
    parser.add_argument("target", nargs="?", default=None, help="Target URL (for single-pass inspection)")
    parser.add_argument("--raw", help="Path to raw server HTML file", default=None)
    parser.add_argument("--rendered", help="Path to rendered DOM HTML file", default=None)
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    if args.raw and args.rendered:
        try:
            with open(args.raw, "r", encoding="utf-8", errors="replace") as fp:
                raw_html = fp.read()
            with open(args.rendered, "r", encoding="utf-8", errors="replace") as fp:
                ren_html = fp.read()
        except OSError as exc:
            sys.stderr.write(f"Error reading comparison files: {exc}\n")
            return 2
        report = compare_raw_vs_rendered(raw_html, ren_html)
    elif args.target:
        try:
            resp = safe_requests_get(args.target, timeout=15)
            html = decode_response_text(resp)
        except (URLSafetyError, Exception) as exc:
            sys.stderr.write(f"Error fetching target {args.target}: {exc}\n")
            return 2
        report = audit_single_raw_html(html)
    else:
        parser.print_help()
        return 2

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        if "rendering_risk" in report:
            print(f"### Visual Semantics & Rendering Gap Score: {report['score']}/100\n")
            print(f"- Overall Rendering Risk: **{report['rendering_risk']}**")
            print(f"- Word Count: {report['raw_metrics']['words']} raw vs {report['rendered_metrics']['words']} rendered (+{report['discrepancies']['word_growth_pct']}%)")
            print(f"- Links: {report['raw_metrics']['links']} raw vs {report['rendered_metrics']['links']} rendered ({report['discrepancies']['links_missing_in_raw_count']} hidden client-side)")
            print(f"- Headings: {report['discrepancies']['h2_missing_in_raw_count']} H2s missing from server HTML\n")

            if report["findings"]:
                print("#### Rendering Discrepancies:")
                for f in report["findings"]:
                    icon = "🔴" if f["severity"] == "CRITICAL" else ("🟠" if f["severity"] == "HIGH" else "🟡")
                    print(f"{icon} [{f['severity']}] {f['detail']}")
        else:
            print(f"### Server HTML Inspection: {report['word_count']} words, {report['link_count']} links")
            print(f"- Empty SPA Root: {'Yes' if report['empty_spa_root_detected'] else 'No'}")
            print(f"- Client-Side Vulnerability: {'Yes' if report['client_side_vulnerability_detected'] else 'No'}")
            print(f"- Recommendation: {report['recommendation']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
