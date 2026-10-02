# OpenSEO Account Setup & MCP Integration

Step-by-step guide to connecting OpenSEO (https://app.openseo.so) into Agy-SEO and Antigravity.

## 1. What is OpenSEO?

OpenSEO is an open-source SEO platform and hosted service (https://app.openseo.so) powered by DataForSEO under the hood. It exposes a native Model Context Protocol (MCP) server that provides AI agents with direct access to:

- Keyword research (search volume, difficulty, intent, CPC, SERP overlap)
- Live Google SERP scraping and organic ranking checks
- Rank tracking and historical position monitoring
- Competitor domain overviews and keyword gap discovery
- Backlink analysis (referring domains, authority, anchor distribution)
- Site audits (crawling, technical and on-page issue detection)
- Google Search Console integration (read-only queries, clicks, impressions)
- AI visibility tracking (Google AI Overviews citations and prompt explorer)

## 2. Obtain Your API Key

1. Log in to https://app.openseo.so (or create an account).
2. Go to **Settings > API keys** (https://app.openseo.so/settings/api-keys).
3. Click **Create API key** and give it a label (e.g. `Agy-SEO-Agent`).
4. Copy the generated key (`oseo_...`). Note: it is only shown once upon creation.

## 3. Configuration in Antigravity

In `C:\Users\mosta\.gemini\config\mcp_config.json`:

```json
{
  "mcpServers": {
    "openseo": {
      "url": "https://app.openseo.so/mcp",
      "headers": {
        "Authorization": "Bearer oseo_YOUR_KEY_HERE"
      }
    }
  }
}
```

## 4. Configuration in Claude Code / Agy-SEO

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "openseo": {
      "url": "https://app.openseo.so/mcp",
      "headers": {
        "Authorization": "Bearer oseo_YOUR_KEY_HERE"
      }
    }
  }
}
```

Or run the automated installer:
```powershell
.\extensions\openseo\install.ps1
```

## 5. Security & Credit Guidelines

- API keys provide full read/write access to your OpenSEO workspace and connected data.
- Never commit API keys to version control.
- OpenSEO queries consume DataForSEO credits on demand. Use targeted keyword queries and domain batching to conserve quota.
