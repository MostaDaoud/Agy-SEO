#!/usr/bin/env python3
"""
WebMCP & Agentic Commerce Readiness Linter.

Audits web pages for Google WebMCP declarations, machine-readable agentic forms,
and Schema.org action contracts (OrderAction, BuyAction, ReserveAction) that let
autonomous AI agents purchase products or book appointments on your site.

Usage:
    python scripts/webmcp_lint.py https://example.com/checkout
    python scripts/webmcp_lint.py form.html --file
    python scripts/webmcp_lint.py form.html --file --json
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


def audit_webmcp_agentic(html: str) -> Dict[str, Any]:
    """Audit HTML for WebMCP and agentic interaction readiness."""
    findings = []
    tools_declared = []

    # 1. Check for explicit WebMCP meta tags or data attributes
    webmcp_meta = re.findall(r'<meta[^>]*name=["\'](?:webmcp:[^"\']+|agentic:[^"\']*)["\'][^>]*>', html, re.I)
    webmcp_forms = re.findall(r'<form\b[^>]*(?:data-webmcp|data-agent|tool-name)=["\'][^"\']+["\'][^>]*>', html, re.I)

    has_explicit_webmcp = bool(webmcp_meta or webmcp_forms)
    if has_explicit_webmcp:
        tools_declared.append("Declarative WebMCP Form Markup")

    # 2. Check for Schema.org potentialAction / Action declarations
    potential_actions = re.findall(r'"@type"\s*:\s*"(OrderAction|BuyAction|ReserveAction|ScheduleAction|TakeAction)"', html, re.I)
    if potential_actions:
        tools_declared.extend(potential_actions)

    # 3. Form Semantic Quality (Inspection of standard HTML forms)
    forms = re.findall(r'<form\b[^>]*>(.*?)</form>', html, re.I | re.S)
    accessible_forms_count = 0
    form_issues = []

    for idx, f in enumerate(forms, 1):
        inputs = re.findall(r'<input\b[^>]*>', f, re.I)
        named_inputs = [inp for inp in inputs if re.search(r'name=["\'][^"\']+["\']', inp)]
        has_submit = bool(re.search(r'type=["\']submit["\']|<button\b', f, re.I))

        # Check if form has semantic names and a submit action
        if inputs and len(named_inputs) == len(inputs) and has_submit:
            accessible_forms_count += 1
        elif inputs and len(named_inputs) < len(inputs):
            form_issues.append(f"Form #{idx}: {len(inputs) - len(named_inputs)} input(s) missing name attributes.")

    # 4. Check for Captcha / Anti-Bot friction that breaks agentic flows
    has_blocking_captcha = bool(
        re.search(r'class=["\'][^"\']*(?:g-recaptcha|h-captcha|cf-turnstile)[^"\']*["\']', html, re.I)
        or re.search(r'recaptcha/api\.js', html, re.I)
    )

    # Calculate Score
    score = 40  # Baseline
    if has_explicit_webmcp:
        score += 30
    if potential_actions:
        score += 20
    if forms and accessible_forms_count == len(forms):
        score += 10

    if has_blocking_captcha and not has_explicit_webmcp:
        findings.append({
            "severity": "WARNING",
            "title": "Unauthenticated Bot Defense on Conversion Flow",
            "detail": "Form relies on client-side CAPTCHA without an authenticated WebMCP agentic alternative. AI agents cannot complete checkout.",
        })

    if not has_explicit_webmcp and not potential_actions:
        findings.append({
            "severity": "OPPORTUNITY",
            "title": "Missing WebMCP / Action Schema Contracts",
            "detail": "Site does not publish declarative WebMCP contracts or OrderAction/ReserveAction schema. AI agents must guess form structure.",
            "fix": "Add declarative data-webmcp='true' attributes or Schema potentialAction to high-intent booking/purchase forms.",
        })

    recommendations = []
    if not has_explicit_webmcp:
        recommendations.append("Add data-webmcp-tool='book_appointment' or 'checkout' annotations to your primary conversion form.")
    if not potential_actions:
        recommendations.append("Inject Schema.org potentialAction (OrderAction or ReserveAction) linking to the action endpoint.")
    if form_issues:
        recommendations.extend(form_issues)

    return {
        "score": min(100, score),
        "status": "READY" if score >= 80 else ("PARTIAL" if score >= 50 else "UNPREPARED"),
        "has_explicit_webmcp": has_explicit_webmcp,
        "tools_declared": tools_declared,
        "total_forms": len(forms),
        "accessible_forms": accessible_forms_count,
        "has_blocking_captcha": has_blocking_captcha,
        "findings": findings,
        "recommendations": recommendations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit web page for WebMCP declarations and Agentic Commerce readiness."
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

    report = audit_webmcp_agentic(html)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"### WebMCP & Agentic Commerce Score: {report['score']}/100 ({report['status']})\n")
        print(f"- Declarative WebMCP Present: {'Yes' if report['has_explicit_webmcp'] else 'No'}")
        print(f"- Declared Agent Tools: {', '.join(report['tools_declared']) if report['tools_declared'] else 'None'}")
        print(f"- Total Forms: {report['total_forms']} ({report['accessible_forms']} with complete semantic names)")
        print(f"- CAPTCHA Barrier Detected: {'Yes (May block autonomous agentic checkout)' if report['has_blocking_captcha'] else 'No'}\n")

        if report["findings"]:
            print("#### Findings:")
            for f in report["findings"]:
                badge = "🟠" if f["severity"] == "WARNING" else "💡"
                print(f"- {badge} [{f['severity']}] {f['title']}: {f['detail']}")

        if report["recommendations"]:
            print("\n#### Recommended Next Steps:")
            for rec in report["recommendations"]:
                print(f"- {rec}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
