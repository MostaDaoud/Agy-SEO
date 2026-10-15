from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import webmcp_lint as wml


def test_declarative_webmcp_form_and_action_detected() -> None:
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Consultation Booking</title>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": "Consultation",
            "potentialAction": {
                "@type": "ReserveAction",
                "target": "https://example.com/book"
            }
        }
        </script>
    </head>
    <body>
        <h1>Book an Appointment</h1>
        <form action="/book" method="POST" data-webmcp="true" tool-name="book_consultation">
            <input type="text" name="client_name" required>
            <input type="date" name="preferred_date" required>
            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    """
    result = wml.audit_webmcp_agentic(html)
    assert result["score"] >= 80
    assert result["has_explicit_webmcp"] is True
    assert "ReserveAction" in result["tools_declared"]
    assert result["status"] == "READY"


def test_unannotated_form_has_low_score() -> None:
    html = """
    <html>
    <body>
        <form action="/login" method="POST">
            <input type="text" name="user">
            <input type="password" name="pass">
            <button type="submit">Login</button>
        </form>
    </body>
    </html>
    """
    result = wml.audit_webmcp_agentic(html)
    assert result["has_explicit_webmcp"] is False
    assert result["score"] <= 50
