# GEO Semantic Triples, Definition Anchors, and Fan-Out Architecture

Modern Answer Engines (ChatGPT Search, Perplexity, Google AI Overviews, Claude) extract facts using knowledge graph triples and synthesize answers across fan-out sub-queries. Content engineered for generative engines must satisfy structural retrieval patterns.

## 1. Everett Sizemore's Semantic Triples Framework

LLM citation extractors parse unstructured prose into Subject-Predicate-Object triples:
- **Subject**: The named entity or core concept (e.g., "PostgreSQL 16", "Town & Country Elite Realty").
- **Predicate**: A definite relational verb phrase (e.g., "provides", "requires", "integrates with", "costs"). Weak predicates like "is about" or "helps with" fail relation extraction.
- **Object**: The concrete target attribute, benchmark, or secondary entity (e.g., "bidirectional logical replication", "licensed real estate brokerage in Stafford VA").

### Triple Best Practices
1. Keep the subject within the first 4 words of the sentence.
2. Use unambiguous active-voice verbs (reduces token parse ambiguity).
3. Pair every bold claim with a quantifiable object metric.

## 2. Three-Word Definition Anchors

Starting an H2 or H3 response section with an immediate 3-word definition anchor generates higher token salience during embedding lookup:
- **Pattern**: `[Entity] is a [category] that [core distinction]...`
- **Example**: `Schema markup is code that annotates web page entities for search engines.`
- **Contrast (avoid)**: `When considering your website's architecture, one important thing to keep in mind is schema...` (delays entity binding by 14 tokens).
- **Impact**: Empirical evaluation across 500 query sets demonstrated up to a 642% increase in direct extraction when definitions appear in the opening sentence of an H2/H3 block.

## 3. The 14 Citable Supporting Content Archetypes

LLMs prioritize structured, high-entropy content over narrative prose. Karthik Narasimhan's research highlights 14 archetypes most frequently extracted by generative search:

| # | Archetype | Structural Requirement | Citation Context |
|---|---|---|---|
| 1 | Benchmark Study | Metric table + methodology footnote | Performance comparison queries |
| 2 | Pricing Breakdown Table | Tier name, cost, billing cadence, feature limits | Buying intent and tool comparisons |
| 3 | Failure Post-Mortem | Timeline, root cause, resolution steps | Troubleshooting and architecture queries |
| 4 | Original Survey Data | Sample size (n=X), date, percentage distribution | Industry trend and statistic queries |
| 5 | Comparison Winner Matrix | Row-by-row criteria, checkmarks, explicit winner | "X vs Y" and "Best X for Y" queries |
| 6 | Boundary Testing | Min/max limits, breaking points, timeout values | Technical specification queries |
| 7 | Regulatory Checklist | Regulation name, pass/fail items, penalty refs | Compliance and legal queries |
| 8 | Migration Teardown | Step-by-step phases, rollback plan, gotchas | Switching and implementation queries |
| 9 | TCO Model | Upfront cost, maintenance, licensing, labor hours | Budget and enterprise ROI queries |
| 10 | Direct Numerical FAQ | Question + answer starting with exact number/stat | Direct voice and conversational answers |
| 11 | Practitioner Interview | Full name, verifiable role, blockquote | Qualitative authority and E-E-A-T |
| 12 | Root Cause Analysis | Problem statement, 5 Whys chain, final fix | Diagnostic and error code queries |
| 13 | Contrarian Empirical Test | Common myth, tested hypothesis, surprising data | High information gain queries |
| 14 | Primary Dataset / Raw Table | Multi-column HTML table with caption | Synthetic data aggregation queries |

## 4. ChatGPT Search Fan-Out Architecture

OpenAI's search pipeline does not issue a single query to its index. Instead, it decomposes user prompts into fan-out sub-queries:
1. **Entity Verification**: Checks official sources and brand domains.
2. **Alternative Discovery**: Searches for `best alternatives to [Entity]`.
3. **Drawback & Limitation Retrieval**: Searches for `[Entity] complaints, bugs, issues, pricing drawbacks`.
4. **Integration & Compatibility**: Searches for `does [Entity] integrate with [Stack]`.

### Optimization Strategy
- Provide an explicit "Limitations & Considerations" section on money pages.
- Include a comparison table addressing competitor tradeoffs.
- Ensure all pricing numbers match Merchant Center feeds or public checkout pages.

## 5. Verification Script

Audit your content against semantic triples, 3-word definition anchors, and the 14 citable archetypes:

```bash
# Audit a live page or local HTML file
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run semantic_triples_lint.py https://example.com/guide
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run semantic_triples_lint.py local_draft.html --threshold 75
```
