# OpenSEO Query Patterns & Best Practices

Workflows for combining OpenSEO live data with Agy-SEO's multi-agent intelligence.

## 1. High-Intent Money Keyword Hunting (Sam Dunning 4+1)

When building bottom-of-funnel keyword lists:
1. Enumerate matrix combinations: `[Competitor] alternatives`, `[Competitor] pricing`, `best [Product] for [Industry]`.
2. Query OpenSEO for volume and keyword difficulty:
   - Low difficulty (KD < 30) with 50-500 monthly searches is ideal.
   - High conversion intent beats broad informational traffic every time.
3. Validate SERP consensus: check if Google returns comparison listicles or product pages.

## 2. Competitive Gap Infiltration

1. Run OpenSEO competitor comparison between target and top 2 direct competitors.
2. Filter for keywords where:
   - Competitors rank in positions 1 to 5.
   - Target domain does not rank (position > 50 or unranked).
   - Commercial or transactional intent is flagged.
3. Feed missing keywords directly into `seo-cluster` for hub-and-spoke topic modeling.

## 3. Backlink Gap & Link Reclamation

1. Pull referring domains for competitor via OpenSEO.
2. Filter for domains with high domain rating (DR > 40) that link to competitors but not target.
3. Categorize by link type:
   - Third-party comparison listicles (prime candidate for mention outreach).
   - Industry directories (immediate submission).
   - Resource pages and blogs (pitch guest expertise or survey data).

## 4. AI Overview Citation Optimization

1. Query target commercial queries in OpenSEO AI Overview Tracker.
2. For queries that trigger AI Overviews:
   - Extract the exact domains cited in the AI summary.
   - Run `seo-geo` against the target page to verify 40-60 word answer-first definition blocks, comparison tables, and structured data schema.
   - Check if cited sources are third-party publications; if so, trigger outreach via `mention-outreach` agent.
