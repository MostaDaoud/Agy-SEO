# OpenSEO MCP Tools Reference

OpenSEO exposes data via the Model Context Protocol (MCP) server at `https://app.openseo.so/mcp`.

## 1. Keyword Research Tools

- **Keyword Overview**: Retrieves search volume, competition level, cost-per-click (CPC), and keyword difficulty (KD score 0-100).
- **Keyword Ideas & Suggestions**: Generates semantic keyword variants, question queries, and long-tail opportunities based on seed keywords.
- **SERP Analysis**: Scrapes real-time organic search results for any query, returning ranks 1-20 with title, URL, snippet, and SERP feature badges (AI Overviews, featured snippets, local packs).

## 2. Domain & Competitor Analysis

- **Domain Overview**: Provides organic search footprint, estimated organic search traffic, and total ranked keyword inventory.
- **Competitor Gap**: Compares target domain against up to 4 competitor domains, identifying keywords where competitors rank in top 10 but target domain is absent.
- **Top Pages**: Returns top traffic-driving URLs for any analyzed domain with keyword counts.

## 3. Backlink Intelligence

- **Backlink Summary**: High-level backlink health: total backlinks, referring domains, referring IPs, dofollow vs nofollow ratio.
- **Referring Domains**: Paginated list of top linking domains with domain authority and first-seen dates.
- **Anchor Text Distribution**: Top anchor text phrases to detect unnatural over-optimization or brand vs commercial anchor balance.

## 4. Rank Tracking & GSC

- **Rank Tracker**: Tracks keyword ranking movements over time across desktop and mobile.
- **Search Console Connector**: Seamless query inspection without Google Cloud API console setup.

## 5. AI Search Citations & Visibility

- **AI Overview Tracker**: Checks whether a brand, domain, or product is cited in Google AI Overviews for target search queries.
- **Prompt Explorer**: Analyzes queries asked to conversational search systems and identifies citation opportunities.
