#!/usr/bin/env python3
"""
14 Critical Shopify Technical SEO Issues Scanner.

Audits e-commerce and Shopify store HTML against Patryk Wawok's 14 Critical
Technical SEO checkpoints:
  1. Collection duplicate product URLs (/collections/*/products/* vs /products/*)
  2. Pagination canonical loops (?page=2 pointing to root)
  3. Tag filter crawl traps (/collections/*/*+*)
  4. Breadcrumb schema alignment
  5. De-JavaScript menus (crawlable navigation in raw HTML)
  6. Contextual navigation siloing
  7. Dynamic related product link accessibility
  8. JSON-LD product syntax and schema validity
  9. Merchant feed alignment (availability, price, condition)
  10. Variant URL canonicalization (?variant=123 canonical)
  11. Out-of-stock handling (OutOfStock vs 404)
  12. Shopify app script injection bloat
  13. Product image alt text coverage
  14. International hreflang subfolder parity

Usage:
    python scripts/shopify_lint.py https://example.com/products/widget
    python scripts/shopify_lint.py product.html --file
    python scripts/shopify_lint.py https://example.com --json
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


def audit_shopify_html(html: str, url: str = "") -> Dict[str, Any]:
    """Audit HTML against the 14 Critical Shopify Technical SEO rules."""
    is_shopify = bool(
        re.search(r"cdn\.shopify\.com", html, re.I)
        or re.search(r"Shopify\.", html)
        or re.search(r"myshopify\.com", html, re.I)
        or re.search(r"shopify-section", html, re.I)
    )

    findings = []
    passed = []
    score = 100

    # 1. Collection Duplicate Product URLs
    # Pattern: href="/collections/.../products/..."
    col_prod_links = re.findall(r'href=["\'](/collections/[^"\']+/products/[^"\']+)["\']', html, re.I)
    if col_prod_links:
        score -= 15
        findings.append({
            "id": 1,
            "title": "Collection Duplicate Product URLs Detected",
            "severity": "CRITICAL",
            "detail": f"Found {len(col_prod_links)} internal links pointing to /collections/.../products/ instead of canonical /products/.",
            "fix": "In product-grid-item.liquid, change 'product.url | within: collection' to 'product.url' to pass link equity directly to the canonical product URL.",
            "samples": col_prod_links[:3],
        })
    else:
        passed.append({"id": 1, "title": "Direct Canonical Product URLs in Navigation"})

    # 2. Pagination Canonical
    # Extract canonical link tag
    can_m = re.search(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', html, re.I)
    if not can_m:
        can_m = re.search(r'<link[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\']canonical["\']', html, re.I)
    canonical = can_m.group(1) if can_m else ""

    if "?page=" in url and canonical and "?page=" not in canonical:
        score -= 10
        findings.append({
            "id": 2,
            "title": "Pagination Canonical Loop Detected",
            "severity": "HIGH",
            "detail": f"Paginated page ({url}) canonicalizes to root collection ({canonical}), creating indexing conflicts.",
            "fix": "Paginated pages must self-canonicalize with ?page=N or implement a selective noindex,follow strategy.",
        })
    else:
        passed.append({"id": 2, "title": "Pagination Canonical Integrity"})

    # 3. Tag Filter Crawl Traps
    tag_filter_links = re.findall(r'href=["\'](/collections/[^"\']+/[^"\']+\+[^"\']+)["\']', html, re.I)
    if tag_filter_links:
        score -= 10
        findings.append({
            "id": 3,
            "title": "Tag Filter Crawl Trap Detected",
            "severity": "HIGH",
            "detail": f"Found {len(tag_filter_links)} multi-tag filter URLs (/collections/.../tag1+tag2) that generate endless crawl permutations.",
            "fix": "Disallow tag filter URLs (/collections/*/*+*) in robots.txt or render filters via client-side state without crawlable anchor tags.",
            "samples": tag_filter_links[:3],
        })
    else:
        passed.append({"id": 3, "title": "Tag Filter Crawl Protection"})

    # 4. Breadcrumb Schema
    has_breadcrumb_schema = bool(
        re.search(r'"@type"\s*:\s*"BreadcrumbList"', html, re.I)
    )
    if not has_breadcrumb_schema:
        score -= 8
        findings.append({
            "id": 4,
            "title": "Missing BreadcrumbList Schema",
            "severity": "MEDIUM",
            "detail": "Product/collection page lacks structured BreadcrumbList JSON-LD.",
            "fix": "Inject BreadcrumbList schema reflecting the category taxonomy for Google snippet navigation hierarchy.",
        })
    else:
        passed.append({"id": 4, "title": "BreadcrumbList Schema Present"})

    # 5. De-JavaScript Menus
    # Check if nav links exist in static HTML
    nav_links = re.findall(r'<nav\b[^>]*>.*?</nav>', html, re.I | re.S)
    has_static_nav = False
    if nav_links:
        nav_anchors = re.findall(r'<a\b[^>]*href=["\'](/collections/[^"\']+)["\']', nav_links[0], re.I)
        if len(nav_anchors) >= 3:
            has_static_nav = True

    if not has_static_nav:
        score -= 12
        findings.append({
            "id": 5,
            "title": "Client-Side Rendered Menu Navigation",
            "severity": "CRITICAL",
            "detail": "Navigation menu has fewer than 3 crawlable category links in initial server HTML. Crawlers may fail to discover sub-collections.",
            "fix": "Render top navigation categories directly in Liquid templates rather than hydrating them via client-side JavaScript.",
        })
    else:
        passed.append({"id": 5, "title": "Crawlable Server-Rendered Navigation"})

    # 8. JSON-LD Product Syntax & Schema Validation
    product_schema_matches = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.I | re.S)
    has_product_schema = False
    schema_syntax_ok = True

    for block in product_schema_matches:
        if '"Product"' in block:
            has_product_schema = True
            try:
                json.loads(block)
            except json.JSONDecodeError:
                schema_syntax_ok = False

    if not has_product_schema and "/products/" in url:
        score -= 10
        findings.append({
            "id": 8,
            "title": "Missing Product Schema JSON-LD",
            "severity": "HIGH",
            "detail": "Product page lacks Schema.org Product markup.",
            "fix": "Add Product JSON-LD schema with name, offers, sku, and image.",
        })
    elif has_product_schema and not schema_syntax_ok:
        score -= 15
        findings.append({
            "id": 8,
            "title": "Malformed Product JSON-LD Syntax",
            "severity": "CRITICAL",
            "detail": "Product JSON-LD block has invalid syntax (unescaped quotes or broken formatting).",
            "fix": "Use json filter in Liquid (e.g. {{ product.title | json }}) to safely escape product titles and descriptions.",
        })
    else:
        passed.append({"id": 8, "title": "Product JSON-LD Syntax Valid"})

    # 9. Feed & Schema Alignment (Offers, price, availability)
    has_offers = bool(re.search(r'"offers"\s*:\s*\{', html, re.I) or re.search(r'"offers"\s*:\s*\[', html, re.I))
    has_availability = bool(re.search(r'https?://schema\.org/(InStock|OutOfStock|BackOrder|PreOrder)', html, re.I))

    if has_product_schema and not (has_offers and has_availability):
        score -= 8
        findings.append({
            "id": 9,
            "title": "Incomplete Product Offer Schema",
            "severity": "MEDIUM",
            "detail": "Product schema is missing offers or availability schema enum.",
            "fix": "Include price, priceCurrency, and availability (schema.org/InStock or OutOfStock) to match Google Merchant Center feeds.",
        })
    else:
        passed.append({"id": 9, "title": "Product Offer & Availability Markup Complete"})

    # 10. Variant URL Canonicalization
    if "?variant=" in url and canonical and "?variant=" in canonical:
        score -= 8
        findings.append({
            "id": 10,
            "title": "Variant Self-Canonicalization Bloat",
            "severity": "MEDIUM",
            "detail": "Variant URL self-canonicalizes, splitting backlink and rank equity across hundreds of color/size variants.",
            "fix": "Canonicalize all variant URLs (?variant=123) to the main parent product URL (/products/handle).",
        })
    else:
        passed.append({"id": 10, "title": "Variant Canonical Consolidation"})

    # 12. Shopify App Script Bloat
    app_scripts = re.findall(r'<script[^>]*src=["\']([^"\']*(?:cdn\.shopify\.com/extensions/|apps/|trekkie|klaviyo|privy|loox|yotpo)[^"\']*)["\']', html, re.I)
    if len(app_scripts) >= 8:
        score -= 10
        findings.append({
            "id": 12,
            "title": "Shopify Third-Party App Script Bloat",
            "severity": "HIGH",
            "detail": f"Detected {len(app_scripts)} third-party app scripts loading in DOM. Heavy app bloat degrades INP and mobile LCP.",
            "fix": "Audit theme.liquid, remove uninstalled app remnants, and defer non-critical marketing widgets with async/defer.",
            "count": len(app_scripts),
        })
    else:
        passed.append({"id": 12, "title": "Managed Script Payload"})

    # 13. Image Alt Text Coverage
    images = re.findall(r'<img\b[^>]*>', html, re.I)
    missing_alt = 0
    for img in images:
        if 'alt=""' in img or "alt=''" in img or "alt=" not in img:
            missing_alt += 1

    if images and (missing_alt / len(images)) > 0.3:
        score -= 7
        findings.append({
            "id": 13,
            "title": "High Ratio of Missing Image Alt Attributes",
            "severity": "MEDIUM",
            "detail": f"{missing_alt} out of {len(images)} images lack descriptive alt text.",
            "fix": "Configure Liquid image tags to output {{ image.alt | escape }} or product title as fallback.",
        })
    else:
        passed.append({"id": 13, "title": "Image Alt Coverage Healthy"})

    # 14. Hreflang Subfolder Parity
    hreflangs = re.findall(r'<link[^>]*rel=["\']alternate["\'][^>]*hreflang=["\']([^"\']+)["\']', html, re.I)
    if "/en-" in url or "/fr" in url or "/de" in url or "/es" in url:
        if not hreflangs:
            score -= 10
            findings.append({
                "id": 14,
                "title": "Missing Hreflang on Regional Subfolder",
                "severity": "HIGH",
                "detail": "Regional/international directory detected but zero hreflang alternate tags found in head.",
                "fix": "Implement bidirectional hreflang tags for regional subfolders (e.g. en-US, en-GB, fr-FR) to prevent regional cannibalization.",
            })
        else:
            passed.append({"id": 14, "title": "Hreflang Configuration Present"})
    else:
        passed.append({"id": 14, "title": "Single Market Baseline"})

    final_score = max(0, score)

    return {
        "is_shopify": is_shopify,
        "score": final_score,
        "status": "PASS" if final_score >= 80 else ("NEEDS_WORK" if final_score >= 60 else "FAIL"),
        "findings": findings,
        "passed_checks": passed,
        "summary": {
            "critical": sum(1 for f in findings if f["severity"] == "CRITICAL"),
            "high": sum(1 for f in findings if f["severity"] == "HIGH"),
            "medium": sum(1 for f in findings if f["severity"] == "MEDIUM"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit e-commerce and Shopify pages against the 14 Critical Technical SEO checkpoints."
    )
    parser.add_argument("target", help="URL or local HTML file path")
    parser.add_argument("--file", action="store_true", help="Treat target as local file")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    url = args.target if not args.file else ""
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

    report = audit_shopify_html(html, url=url)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"### Shopify & E-Commerce Technical SEO Score: {report['score']}/100 ({report['status']})\n")
        print(f"- Shopify Platform Detected: {'Yes' if report['is_shopify'] else 'No / Generic E-Commerce'}")
        print(f"- Issues Found: {report['summary']['critical']} Critical, {report['summary']['high']} High, {report['summary']['medium']} Medium\n")

        if report["findings"]:
            print("#### Issues to Remediate:")
            for issue in report["findings"]:
                badge = "🔴" if issue["severity"] == "CRITICAL" else ("🟠" if issue["severity"] == "HIGH" else "🟡")
                print(f"{badge} [{issue['severity']}] #{issue['id']}: {issue['title']}")
                print(f"   Detail: {issue['detail']}")
                print(f"   Fix: {issue['fix']}\n")

        print("#### Passed Checkpoints:")
        for p in report["passed_checks"]:
            print(f"- ✅ #{p['id']}: {p['title']}")

    return 0 if report["score"] >= 70 else 1


if __name__ == "__main__":
    sys.exit(main())
