# SEO Playground Dashboard Integration Guide

## Overview

[SEO Playground](https://github.com/paulmassen/seo-playground) (by Paul Massendari) is a self-hosted, open-source Next.js 14 web dashboard that provides an interactive visual interface over 40+ DataForSEO tools. All query results are cached locally in an embedded SQLite database (`./data/`), eliminating duplicate API costs when reviewing historical audits, rankings, or geo-grids.

Agy-SEO pairs with SEO Playground as complementary tools:
- **Agy-SEO / Antigravity:** Autonomous CLI and agentic execution engine, parallel headless crawling, dual SEO + GEO analysis, and prompt engineering.
- **SEO Playground:** Visual web UI for interactive geo-grid heatmaps, review charts, and historical rank trend monitoring.

## Key Features

1. **Geo-Grid Visual Heatmaps:** Visual 3x3 to 11x11 ranking heatmaps with point-by-point movement across historical runs.
2. **Review Rating Goal Visualizer:** Interactive breakdown of review ratings and the exact number of 5-star reviews needed to reach milestone display ratings on Google Maps.
3. **Queue Mode Cost Tiering:** Choose between Live, Priority (40% discount), and Standard Queue (70% discount) for batch geo-grid scans.
4. **DataForSEO Spend Tracking:** Granular accounting of credit spending per tool and date range.
5. **Multi-Project Workspace:** Switch between clients or domains with separate defaults and SQLite search histories.

## Local Deployment

### Option 1: Docker Compose (Recommended)

Clone the repository and launch via Docker:

```bash
git clone https://github.com/paulmassen/seo-playground.git
cd seo-playground
docker compose up -d --build
```

Access the dashboard at `http://localhost:3000`.

### Option 2: Local Node.js Development

Prerequisites: Node.js 18+

```bash
git clone https://github.com/paulmassen/seo-playground.git
cd seo-playground
npm install
npm run dev
```

Open `http://localhost:3000` in your browser.

## Configuration

Navigate to **Settings** in the dashboard and input your DataForSEO API credentials (`login` and `password`). Credentials are encrypted and stored in your local SQLite database in `./data/`.

## Agy-SEO Native Integration

For automated CLI workflows, Agy-SEO integrates these core algorithms natively:
- **Review Rating Goals:**
  ```bash
  "${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run rating_goal.py --rating 4.6 --reviews 82
  ```
- **Maps Rating Goal Subcommand:**
  ```
  /seo maps rating-goal 4.6 82
  ```
