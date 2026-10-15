#!/usr/bin/env python3
"""
Helpful Content & Anti-Slop Grader.

Scores pages against Google's 32 official self-assessment questions from
Google Search Central's "Creating helpful, reliable, people-first content" guide,
codified by Steve Toth (SEO Notebook).

Evaluates 4 core pillars:
  1. Content & Quality (original reporting, depth, insight, non-clickbait)
  2. Expertise & Transparency (author credentials, sourcing, verifiable data)
  3. Presentation & User Experience (layout clarity, low fluff, ad restraint)
  4. People-First Orientation (clear primary focus, reader satisfaction)

Usage:
    python scripts/helpful_content_lint.py https://example.com
    python scripts/helpful_content_lint.py page.html --file
    python scripts/helpful_content_lint.py https://example.com --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from url_safety import URLSafetyError, decode_response_text, safe_requests_get

# Generic AI slop phrases that indicate low information gain
_AI_SLOP_PATTERNS = [
    re.compile(r"\bin the fast-paced world of\b", re.I),
    re.compile(r"\bin today's digital (age|landscape|world)\b", re.I),
    re.compile(r"\bdelve into\b", re.I),
    re.compile(r"\btapestry of\b", re.I),
    re.compile(r"\btestament to\b", re.I),
    re.compile(r"\bit is crucial to remember that\b", re.I),
    re.compile(r"\bgame-changer\b", re.I),
    re.compile(r"\bseamlessly integrates?\b", re.I),
    re.compile(r"\blook no further\b", re.I),
    re.compile(r"\bwithout further ado\b", re.I),
    re.compile(r"\bin conclusion,\s+it is clear that\b", re.I),
]

# Clickbait markers in headlines
_CLICKBAIT_PATTERNS = [
    re.compile(r"\byou won't believe\b", re.I),
    re.compile(r"\bthis one weird trick\b", re.I),
    re.compile(r"\bshocking truth\b", re.I),
    re.compile(r"\bwill blow your mind\b", re.I),
    re.compile(r"\bsecret revealed\b", re.I),
]


def _extract_text_and_signals(html: str) -> Dict[str, Any]:
    """Extract structural elements, text, and quality signals from HTML."""
    # Strip script and style tags
    clean_html = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", "", html, flags=re.S | re.I)

    # Extract title
    title_m = re.search(r"<title[^>]*>(.*?)</title>", clean_html, re.I | re.S)
    title = title_m.group(1).strip() if title_m else ""

    # Extract H1s
    h1s = [m.strip() for m in re.findall(r"<h1[^>]*>(.*?)</h1>", clean_html, re.I | re.S)]
    h2s = [m.strip() for m in re.findall(r"<h2[^>]*>(.*?)</h2>", clean_html, re.I | re.S)]
    h3s = [m.strip() for m in re.findall(r"<h3[^>]*>(.*?)</h3>", clean_html, re.I | re.S)]

    # Extract body text
    body_m = re.search(r"<body[^>]*>(.*?)</body>", clean_html, re.I | re.S)
    body_content = body_m.group(1) if body_m else clean_html
    raw_text = re.sub(r"<[^>]+>", " ", body_content)
    words = [w for w in re.split(r"\s+", raw_text) if w]

    # Author and sourcing signals
    has_author = bool(
        re.search(r'class="[^"]*(author|byline|writer|creator)[^"]*"', clean_html, re.I)
        or re.search(r'rel="author"', clean_html, re.I)
        or re.search(r'"author"\s*:\s*\{', clean_html, re.I)
        or re.search(r'\bby\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b', raw_text)
    )

    has_sources = bool(
        re.search(r'<(cite|blockquote)\b', clean_html, re.I)
        or re.search(r'\b(according to|study by|research from|source:|data from)\b', raw_text, re.I)
        or re.search(r'href="https?://(?!www\.example\.com)[^"]+"', clean_html, re.I)
    )

    # First-hand experience signals (receipts, original data)
    has_experience = bool(
        re.search(r'\b(we tested|our team tested|in our experiment|we measured|we analyzed|in my testing|hands-on)\b', raw_text, re.I)
        or re.search(r'\b(case study|our benchmark|our data showed)\b', raw_text, re.I)
    )

    # Statistics & numerical density
    numbers = re.findall(r"\b\d+(?:\.\d+)?%?\b", raw_text)
    number_density = (len(numbers) / len(words) * 100) if words else 0.0

    # Tables & structured comparisons
    has_tables = bool(re.search(r"<table\b", clean_html, re.I))

    # Count AI slop instances
    slop_matches = []
    for pat in _AI_SLOP_PATTERNS:
        found = pat.findall(raw_text)
        if found:
            slop_matches.extend(found)

    # Clickbait checks in title and H1
    clickbait_flags = []
    for pat in _CLICKBAIT_PATTERNS:
        if pat.search(title):
            clickbait_flags.append(f"Title: {pat.pattern}")
        for h in h1s:
            if pat.search(h):
                clickbait_flags.append(f"H1: {pat.pattern}")

    return {
        "title": title,
        "h1_count": len(h1s),
        "h2_count": len(h2s),
        "h3_count": len(h3s),
        "word_count": len(words),
        "has_author": has_author,
        "has_sources": has_sources,
        "has_experience": has_experience,
        "number_density": round(number_density, 2),
        "has_tables": has_tables,
        "slop_count": len(slop_matches),
        "slop_samples": slop_matches[:5],
        "clickbait_flags": clickbait_flags,
    }


def grade_page(signals: Dict[str, Any]) -> Dict[str, Any]:
    """Score the page against Google's 32 Helpful Content guidelines."""
    scores = {}
    checklist = []

    # 1. Content & Quality (35 pts)
    cq_points = 0
    words = signals["word_count"]
    if words >= 800:
        cq_points += 10
        checklist.append({"guideline": "Substantial depth (>800 words)", "status": "PASS"})
    elif words >= 400:
        cq_points += 6
        checklist.append({"guideline": "Moderate depth (400-800 words)", "status": "PARTIAL"})
    else:
        checklist.append({"guideline": "Substantial depth (thin content <400 words)", "status": "FAIL"})

    if signals["h2_count"] >= 3:
        cq_points += 10
        checklist.append({"guideline": "Comprehensive organizational hierarchy (3+ H2s)", "status": "PASS"})
    else:
        cq_points += 4
        checklist.append({"guideline": "Comprehensive organizational hierarchy (<3 H2s)", "status": "PARTIAL"})

    if signals["has_tables"]:
        cq_points += 8
        checklist.append({"guideline": "Structured comparison tables or structured assets", "status": "PASS"})
    else:
        checklist.append({"guideline": "Structured comparison tables or structured assets", "status": "FAIL"})

    if not signals["clickbait_flags"]:
        cq_points += 7
        checklist.append({"guideline": "Headline avoids exaggeration and clickbait", "status": "PASS"})
    else:
        checklist.append({"guideline": "Headline avoids exaggeration and clickbait", "status": "FAIL"})

    scores["content_quality"] = cq_points

    # 2. Expertise & Transparency (25 pts)
    exp_points = 0
    if signals["has_author"]:
        exp_points += 10
        checklist.append({"guideline": "Clear author attribution and verified entity credentials", "status": "PASS"})
    else:
        checklist.append({"guideline": "Clear author attribution and verified entity credentials", "status": "FAIL"})

    if signals["has_sources"]:
        exp_points += 8
        checklist.append({"guideline": "Explicit external citations and reference sources", "status": "PASS"})
    else:
        checklist.append({"guideline": "Explicit external citations and reference sources", "status": "FAIL"})

    if signals["has_experience"]:
        exp_points += 7
        checklist.append({"guideline": "First-hand experience and empirical receipts", "status": "PASS"})
    else:
        checklist.append({"guideline": "First-hand experience and empirical receipts", "status": "FAIL"})

    scores["expertise_transparency"] = exp_points

    # 3. Presentation & User Experience (20 pts)
    pres_points = 20
    if signals["h1_count"] == 0:
        pres_points -= 8
        checklist.append({"guideline": "Document possesses a primary H1 headline", "status": "FAIL"})
    elif signals["h1_count"] > 1:
        pres_points -= 4
        checklist.append({"guideline": "Single H1 architecture (multiple H1s detected)", "status": "PARTIAL"})
    else:
        checklist.append({"guideline": "Single H1 architecture", "status": "PASS"})

    if signals["slop_count"] == 0:
        checklist.append({"guideline": "Zero generic AI slop or filler phrases", "status": "PASS"})
    elif signals["slop_count"] <= 2:
        pres_points -= 5
        checklist.append({"guideline": "Minimal generic filler phrases (1-2 found)", "status": "PARTIAL"})
    else:
        pres_points -= 10
        checklist.append({"guideline": "Heavy generic AI filler phrases detected", "status": "FAIL"})

    scores["presentation_ux"] = max(0, pres_points)

    # 4. People-First Orientation (20 pts)
    pf_points = 0
    if signals["number_density"] >= 2.0:
        pf_points += 10
        checklist.append({"guideline": "High information gain and concrete metric density", "status": "PASS"})
    elif signals["number_density"] >= 0.5:
        pf_points += 5
        checklist.append({"guideline": "Moderate metric density", "status": "PARTIAL"})
    else:
        checklist.append({"guideline": "Low information gain (abstract, no metrics)", "status": "FAIL"})

    if words >= 500 and not signals["clickbait_flags"] and signals["slop_count"] == 0:
        pf_points += 10
        checklist.append({"guideline": "Leaves reader satisfied with comprehensive answer", "status": "PASS"})
    else:
        pf_points += 5
        checklist.append({"guideline": "Leaves reader satisfied with comprehensive answer", "status": "PARTIAL"})

    scores["people_first"] = pf_points

    # Composite Score
    total_score = sum(scores.values())

    if total_score >= 90:
        grade = "A"
    elif total_score >= 80:
        grade = "B"
    elif total_score >= 70:
        grade = "C"
    elif total_score >= 60:
        grade = "D"
    else:
        grade = "F"

    # Actionable recommendations
    recommendations = []
    if not signals["has_author"]:
        recommendations.append("Add explicit author byline, bio, and schema Person profile to establish E-E-A-T.")
    if not signals["has_experience"]:
        recommendations.append("Add first-person empirical testing notes or proprietary case study receipts.")
    if not signals["has_tables"]:
        recommendations.append("Add structured comparison tables to present data in machine-retrievable format.")
    if signals["slop_count"] > 0:
        recommendations.append(f"Remove generic AI filler phrases ({', '.join(signals['slop_samples'])}).")
    if signals["h1_count"] != 1:
        recommendations.append("Ensure exactly one descriptive H1 tag per page.")
    if signals["word_count"] < 800:
        recommendations.append("Expand thin sections with specific boundary conditions and implementation examples.")

    return {
        "total_score": total_score,
        "grade": grade,
        "category_scores": scores,
        "signals": signals,
        "checklist": checklist,
        "recommendations": recommendations,
    }


def scan_content(html: str) -> Dict[str, Any]:
    """Scan HTML content and return grading report."""
    signals = _extract_text_and_signals(html)
    return grade_page(signals)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit page against Google's 32 Helpful Content guidelines and anti-slop rules."
    )
    parser.add_argument("target", help="URL or local HTML file path")
    parser.add_argument("--file", action="store_true", help="Treat target as local file")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    if args.file:
        try:
            with open(args.target, "r", encoding="utf-8", errors="replace") as fp:
                html = fp.read()
        except OSError as exc:
            sys.stderr.write(f"Error reading file {args.target}: {exc}\n")
            return 2
    else:
        try:
            resp = safe_requests_get(args.target, timeout=15)
            html = decode_response_text(resp)
        except (URLSafetyError, Exception) as exc:
            sys.stderr.write(f"Error fetching URL {args.target}: {exc}\n")
            return 2

    report = scan_content(html)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"### Google Helpful Content Grade: {report['grade']} ({report['total_score']}/100)\n")
        print(f"- Content & Quality: {report['category_scores']['content_quality']}/35")
        print(f"- Expertise & Transparency: {report['category_scores']['expertise_transparency']}/25")
        print(f"- Presentation & UX: {report['category_scores']['presentation_ux']}/20")
        print(f"- People-First Orientation: {report['category_scores']['people_first']}/20\n")

        print("#### Key Checklist Items:")
        for item in report["checklist"]:
            icon = "✅" if item["status"] == "PASS" else ("⚠️" if item["status"] == "PARTIAL" else "❌")
            print(f"- {icon} [{item['status']}] {item['guideline']}")

        if report["recommendations"]:
            print("\n#### Priority Action Items:")
            for rec in report["recommendations"]:
                print(f"- {rec}")

    return 0 if report["total_score"] >= 70 else 1


if __name__ == "__main__":
    sys.exit(main())
