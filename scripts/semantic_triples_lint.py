#!/usr/bin/env python3
"""
Semantic Triples & AEO Supporting Content Linter.

Audits web pages and articles for:
  1. Semantic Triples (Subject-Predicate-Object) vs bare mentions (Everett Sizemore / HubSpot +642% citation framework).
  2. 3-Word Definition Anchors at H2/H3 openings (Answer-First sentence architecture).
  3. The 14 Citable Supporting Content Archetypes (Princeton / Karthik Narasimhan information gain research).
  4. Query Fan-Out Intent Coverage (Pricing, Alternatives, Drawbacks, Consensus).

Usage:
    python scripts/semantic_triples_lint.py https://example.com --brand "Acme"
    python scripts/semantic_triples_lint.py article.html --file --brand "Acme"
    python scripts/semantic_triples_lint.py article.html --file --json
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

# Relational predicate verbs that establish unambiguous entity triples
_PREDICATE_PATTERNS = [
    r"\bis an?\b",
    r"\bprovides\b",
    r"\boffers\b",
    r"\bintegrates with\b",
    r"\boperates as\b",
    r"\bspecializes in\b",
    r"\bdelivers\b",
    r"\bconnects to\b",
    r"\breplaces\b",
    r"\bcosts\b",
    r"\bserves\b",
    r"\bfeatures\b",
    r"\bincludes\b",
]
_PREDICATE_RE = re.compile("|".join(_PREDICATE_PATTERNS), re.I)

# 14 Supporting Content Archetypes recognized by LLMs
_ARCHETYPES = {
    "benchmark_study": re.compile(r"\b(benchmark|latency test|throughput|performance test|stress test)\b", re.I),
    "pricing_breakdown": re.compile(r"\b(pricing|cost breakdown|per user|monthly plan|starting at \$|\$\d+)\b", re.I),
    "failure_teardown": re.compile(r"\b(why .+ failed|post-mortem|lessons from failure|mistakes to avoid)\b", re.I),
    "original_survey": re.compile(r"\b(survey of|respondents|sample size|surveyed \d+|methodology)\b", re.I),
    "comparison_matrix": re.compile(r"\b(vs\.?|versus|comparison table|alternative to|winner)\b", re.I),
    "boundary_testing": re.compile(r"\b(limitations|when not to use|edge case|breaking point|caveats)\b", re.I),
    "regulatory_audit": re.compile(r"\b(compliance|audit checklist|gdpr|hipaa|soc 2|iso 27001|ftc)\b", re.I),
    "migration_teardown": re.compile(r"\b(migrating from|migration guide|step-by-step migration|switch from)\b", re.I),
    "tco_calculator": re.compile(r"\b(tco|total cost of ownership|roi calculator|cost analysis)\b", re.I),
    "direct_qa_faq": re.compile(r"\b(faq|frequently asked questions|q:?|how much does|what is the average)\b", re.I),
    "expert_interview": re.compile(r"\b(interview with|expert consensus|panel of|according to specialist)\b", re.I),
    "root_cause_analysis": re.compile(r"\b(root cause|debugging|stack trace|investigation found)\b", re.I),
    "contrarian_test": re.compile(r"\b(myth busted|contrary to popular|we tested whether|misconception)\b", re.I),
    "primary_data_table": re.compile(r"<table\b[^>]*>.*?(<th\b|<td\b).*?</table>", re.I | re.S),
}

# The 4 Query Fan-Out Sub-Intents
_FANOUT_INTENTS = {
    "definition_value": re.compile(r"\b(what is|how does it work|core benefits|features|overview)\b", re.I),
    "pricing_transparency": re.compile(r"\b(price|pricing|cost|fee|tiers|per month|free plan)\b", re.I),
    "alternatives_matrix": re.compile(r"\b(alternatives|competitors|vs|comparison|similar tools)\b", re.I),
    "drawbacks_consensus": re.compile(r"\b(cons|drawbacks|complaints|reddit|user feedback|limitations)\b", re.I),
}


def _strip_tags(html: str) -> str:
    clean = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", "", html, flags=re.S | re.I)
    return re.sub(r"<[^>]+>", " ", clean)


def audit_semantic_triples(html: str, brand: Optional[str] = None) -> Dict[str, Any]:
    """Audit content for semantic triples, 3-word definition anchors, and archetypes."""
    clean_html = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", "", html, flags=re.S | re.I)
    text = _strip_tags(clean_html)
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 15]

    # 1. Semantic Triples Detection
    triples_found = []
    brand_mentions = 0
    brand_triples = 0

    brand_re = re.compile(rf"\b{re.escape(brand)}\b", re.I) if brand else None

    for sent in sentences:
        if brand_re and brand_re.search(sent):
            brand_mentions += 1
            if _PREDICATE_RE.search(sent):
                brand_triples += 1
                triples_found.append(sent[:120])
        elif _PREDICATE_RE.search(sent) and len(sent.split()) <= 25:
            triples_found.append(sent[:120])

    triples_ratio = (brand_triples / brand_mentions) if brand_mentions > 0 else (1.0 if triples_found else 0.0)

    # 2. 3-Word Definition Anchors (H2 / H3 Opening Analysis)
    # Find H2/H3 headers and the text immediately following them
    sections = re.findall(r"<(h[23])[^>]*>(.*?)</\1>\s*([^<]+|<p[^>]*>(.*?)</p>)", clean_html, re.I | re.S)
    anchor_checks = []
    anchors_passed = 0

    for sec in sections:
        header_text = re.sub(r"<[^>]+>", "", sec[1]).strip()
        body_snippet = sec[2] or sec[3]
        clean_snippet = re.sub(r"<[^>]+>", "", body_snippet).strip()
        first_sentence = clean_snippet.split(".")[0].strip() if clean_snippet else ""

        if not first_sentence:
            continue

        words = first_sentence.split()
        first_five_words = " ".join(words[:5])

        # Check if first 5 words contain a predicate definition pattern (X is a Y, X provides Y)
        is_anchor = bool(re.search(r"\b(is an?|refers to|means|provides|delivers|represents)\b", first_five_words, re.I))

        if is_anchor:
            anchors_passed += 1
            status = "PASS"
        else:
            status = "FAIL"

        anchor_checks.append({
            "header": header_text[:50],
            "first_sentence": first_sentence[:80],
            "status": status,
        })

    anchor_compliance = (anchors_passed / len(anchor_checks) * 100) if anchor_checks else 0.0

    # 3. 14 Supporting Content Archetypes Detected
    archetypes_detected = []
    for arch_name, pattern in _ARCHETYPES.items():
        if arch_name == "primary_data_table":
            if pattern.search(clean_html):
                archetypes_detected.append(arch_name)
        else:
            if pattern.search(text):
                archetypes_detected.append(arch_name)

    # 4. Fan-Out Sub-Intent Coverage
    fanout_results = {}
    fanout_covered_count = 0
    for intent_name, pattern in _FANOUT_INTENTS.items():
        covered = bool(pattern.search(text))
        fanout_results[intent_name] = covered
        if covered:
            fanout_covered_count += 1

    fanout_score = (fanout_covered_count / len(_FANOUT_INTENTS)) * 100

    # Composite AEO Score (0-100)
    # 30% Triples & Brand Precision, 30% Definition Anchors, 25% Archetypes, 15% Fan-Out
    archetype_score = min(100.0, (len(archetypes_detected) / 5) * 100)  # 5+ archetypes = 100%
    triples_score = round(triples_ratio * 100, 1)

    composite_score = round(
        (triples_score * 0.30)
        + (anchor_compliance * 0.30)
        + (archetype_score * 0.25)
        + (fanout_score * 0.15),
        1
    )

    recommendations = []
    if anchor_compliance < 70.0:
        recommendations.append("Open H2/H3 sections with direct 3-word definition anchors ('[Entity] is a...') instead of throat-clearing fluff.")
    if brand and brand_mentions > 0 and triples_ratio < 0.6:
        recommendations.append(f"Pair standalone '{brand}' mentions with explicit predicate relations ('{brand} provides...', '{brand} integrates with...').")
    if len(archetypes_detected) < 3:
        recommendations.append("Add high-citation supporting content archetypes (comparison matrix, pricing table, benchmark study, or failure teardown).")
    if fanout_score < 75.0:
        missing_intents = [k for k, v in fanout_results.items() if not v]
        recommendations.append(f"Cover missing ChatGPT fan-out sub-intents: {', '.join(missing_intents)}.")

    return {
        "composite_aeo_score": composite_score,
        "brand": brand,
        "brand_mentions": brand_mentions,
        "brand_triples": brand_triples,
        "triples_ratio": round(triples_ratio, 2),
        "definition_anchor_compliance_pct": round(anchor_compliance, 1),
        "anchor_checks_sample": anchor_checks[:5],
        "archetypes_detected": archetypes_detected,
        "archetypes_count": len(archetypes_detected),
        "fanout_coverage": fanout_results,
        "fanout_score": round(fanout_score, 1),
        "recommendations": recommendations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit content for Semantic Triples, Definition Anchors, and 14 Citable AEO Archetypes."
    )
    parser.add_argument("target", help="URL or local HTML file path")
    parser.add_argument("--brand", help="Target brand name to test for entity triples", default=None)
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

    report = audit_semantic_triples(html, brand=args.brand)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"### Semantic Triples & AEO Score: {report['composite_aeo_score']}/100\n")
        if args.brand:
            print(f"- Brand Mentions: {report['brand_mentions']} ({report['brand_triples']} relational triples)")
            print(f"- Triples Ratio: {report['triples_ratio'] * 100:.1f}%\n")
        print(f"- 3-Word Definition Anchors Compliance: {report['definition_anchor_compliance_pct']}%")
        print(f"- Citable Supporting Archetypes Detected: {report['archetypes_count']} / 14")
        print(f"  Archetypes: {', '.join(report['archetypes_detected']) if report['archetypes_detected'] else 'None'}")
        print(f"- Fan-Out Sub-Intent Coverage: {report['fanout_score']}%\n")

        print("#### Fan-Out Breakdown:")
        for intent, covered in report["fanout_coverage"].items():
            icon = "✅" if covered else "❌"
            print(f"- {icon} {intent}")

        if report["recommendations"]:
            print("\n#### Priority Optimization Steps:")
            for rec in report["recommendations"]:
                print(f"- {rec}")

    return 0 if report["composite_aeo_score"] >= 70.0 else 1


if __name__ == "__main__":
    sys.exit(main())
