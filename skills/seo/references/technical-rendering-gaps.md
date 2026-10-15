# Technical Rendering Gaps: Raw HTML vs Rendered DOM

Modern search engines and AI answer engines operate on strict computing budgets. While Google eventually executes client-side JavaScript through its Web Rendering Service (WRS), AI search bots (GPTBot, PerplexityBot, ClaudeBot) frequently skip heavy client-side execution. This gap between Raw Server HTML and Rendered DOM represents a primary failure mode in modern SEO.

## The Dual-Wave Crawling Architecture

1. **Wave 1 (HTTP Response Fetch)**: The crawler requests the page and immediately parses raw server-side HTML. Internal links, meta robots directives, canonical tags, and structured data present in this initial byte stream are indexed instantly.
2. **Wave 2 (Headless Browser Execution)**: The page is queued for headless rendering. If JavaScript execution exceeds timeout limits (typically 5 seconds) or crashes due to client-side exceptions, the page is indexed strictly based on Wave 1.

## Critical Discrepancy Classes (Koray Tuğberk Gübür & Kunjal Chawhan Framework)

| Category | Raw State (Server) | Rendered State (DOM) | Risk & Impact |
|---|---|---|---|
| Internal Links | Missing or empty container | Injected via client-side framework | Critical: Crawlers fail to discover child pages during Wave 1 |
| Primary Heading | Missing or placeholder `<h1>` | Hydrated from client-side state | High: Topic classification delayed or misclassified |
| Canonical URL | `<link rel="canonical" href="...">` | Mutated by client-side router | Critical: Duplicate content indexation loops |
| Meta Robots | `index, follow` | Script injects `noindex` (or vice versa) | High: Accidental de-indexing or indexing of private pages |
| Schema Markup | Absent from raw HTML | Injected via GTM / client-side hook | High: AI engines fail to extract relational knowledge graph |
| Core Content | Spinner / loading skeleton | Rendered after API promise resolves | Critical: Search engines treat page as thin or soft 404 |

## AI Search Crawler Limitations

AI search bots like PerplexityBot and GPTBot prioritize speed and lower resource consumption over complete browser rendering:
- **No Headless Execution**: Many AI retrieval bots run fast text extractors that do not execute client-side JavaScript.
- **Accordion and Hidden Content**: Content hidden behind click events or accordion tabs that require client JavaScript state changes may never be extracted for citations.
- **Timeout Vulnerability**: Heavy JavaScript hydration that takes >2.5s on mobile CPUs will fail to provide data to real-time generative search pipelines.

## Audit and Remediation Protocol

1. **Compare Raw vs Rendered**:
   - Extract raw HTML via direct HTTP GET request.
   - Extract rendered DOM via headless Chrome (Puppeteer / Playwright).
   - Compute link count delta, heading count delta, and schema presence delta.
2. **Shift to Server-Side Rendering (SSR) or Static Site Generation (SSG)**:
   - Ensure all primary navigation links exist in raw server HTML `<a href="...">` tags.
   - Never inject schema markup solely through client-side Tag Managers. Place JSON-LD directly into the server response `<head>`.
3. **Verify Zero Dynamic Heading Swaps**:
   - The raw HTML must declare the exact primary `<h1>` and section `<h2>` hierarchy. Avoid hydrating headings from asynchronous API payloads.

## Automated Rendering Gap Tool

Use the discrepancy linter to compare raw HTTP response against headless rendered DOM:

```bash
# Compare live URL raw HTML vs rendered DOM
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run rendering_gap_lint.py https://example.com/page
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run rendering_gap_lint.py https://example.com/app --wait 3000
```
