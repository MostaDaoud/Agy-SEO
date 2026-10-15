from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import semantic_triples_lint as stl


def test_semantic_triples_and_definition_anchors_detected() -> None:
    html = """
    <html>
    <body>
        <h1>Enterprise Vector Database Architecture</h1>
        <h2>PostgreSQL pgvector Architecture</h2>
        <p>pgvector is an open-source extension that provides vector similarity search inside PostgreSQL.</p>
        <p>Acme Corp integrates with pgvector and delivers sub-10ms nearest neighbor search.</p>
        
        <h2>Benchmark Study and Performance Test</h2>
        <p>Our benchmark study conducted a stress test evaluating 1,000,000 embeddings.</p>
        
        <h2>Pricing Breakdown and Cost Model</h2>
        <p>Pricing starts at $49 per user with a transparent monthly plan.</p>
        
        <h2>Limitations and Edge Cases</h2>
        <p>When not to use this system: memory limitations occur beyond 50M vectors.</p>
    </body>
    </html>
    """
    result = stl.audit_semantic_triples(html, brand="Acme Corp")
    assert result["composite_aeo_score"] >= 55
    assert result["brand_triples"] >= 1
    assert result["definition_anchor_compliance_pct"] >= 25.0
    assert "benchmark_study" in result["archetypes_detected"]
    assert "pricing_breakdown" in result["archetypes_detected"]
    assert "boundary_testing" in result["archetypes_detected"]
    assert result["fanout_coverage"]["pricing_transparency"] is True
    assert result["fanout_coverage"]["drawbacks_consensus"] is True


def test_bare_mentions_without_predicates_flagged() -> None:
    html = """
    <html>
    <body>
        <h1>Unstructured Discussion</h1>
        <h2>General Overview</h2>
        <p>Around here we often talk about Acme Corp. Acme Corp is there. Lots of people like Acme Corp in the community.</p>
    </body>
    </html>
    """
    result = stl.audit_semantic_triples(html, brand="Acme Corp")
    assert result["brand_mentions"] >= 1
    assert result["triples_ratio"] < 0.6
