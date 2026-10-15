from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import shopify_lint as sl


def test_clean_storefront_scores_high() -> None:
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="canonical" href="https://shop.example.com/products/running-shoe">
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "Product",
                    "name": "Pro Running Shoe",
                    "offers": {
                        "@type": "Offer",
                        "price": "120.00",
                        "priceCurrency": "USD",
                        "availability": "https://schema.org/InStock"
                    },
                    "aggregateRating": {
                        "@type": "AggregateRating",
                        "ratingValue": "4.8",
                        "reviewCount": "124"
                    }
                },
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": []
                }
            ]
        }
        </script>
    </head>
    <body>
        <h1>Pro Running Shoe</h1>
        <nav>
            <ul>
                <li><a href="/collections/running-shoes">Running Shoes</a></li>
                <li><a href="/collections/trail-shoes">Trail Shoes</a></li>
                <li><a href="/collections/apparel">Apparel</a></li>
            </ul>
        </nav>
        <div class="product-price">$120.00</div>
    </body>
    </html>
    """
    result = sl.audit_shopify_html(html, url="https://shop.example.com/products/running-shoe")
    assert result["score"] >= 80
    assert result["summary"]["critical"] == 0


def test_shopify_traps_flagged() -> None:
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="canonical" href="https://shop.example.com/collections/frontpage?page=1">
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Budget Shoe",
            "offers": {
                "@type": "Offer",
                "price": "50.00",
                "availability": "https://schema.org/InStock"
            }
        }
        </script>
    </head>
    <body>
        <h1>Store Header</h1>
        <a href="/collections/mens/products/budget-shoe">Budget Shoe (Collection Scoped)</a>
        <a href="/collections/all?page=1">Page 1 Loop</a>
        <a href="/collections/all/red+blue+cotton">Tag Crawl Trap</a>
        <div class="product-price">$89.00</div>
    </body>
    </html>
    """
    result = sl.audit_shopify_html(html, url="https://shop.example.com/collections/all")
    finding_titles = {f["title"] for f in result["findings"]}
    assert "Collection Duplicate Product URLs Detected" in finding_titles
    assert "Tag Filter Crawl Trap Detected" in finding_titles
    assert "Client-Side Rendered Menu Navigation" in finding_titles
    assert result["summary"]["critical"] >= 1
