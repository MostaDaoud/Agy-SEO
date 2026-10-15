# WebMCP: Declarative Agentic Commerce and Tool Registration

WebMCP (Web Model Context Protocol) bridges web applications and autonomous AI agents (such as ChatGPT desktop, Chrome agent extensions, and conversational copilots). By exposing structured tool interfaces, web applications allow AI agents to navigate forms, execute bookings, and complete transactions deterministically without fragile UI scraping.

## The Dual WebMCP Implementation Architecture

WebMCP supports two implementation modalities:
1. **Imperative Tool Registration**: JavaScript-driven via `document.modelContext.registerTool()`. Ideal for complex multi-step workflows, authenticated operations, and dynamic API responses.
2. **Declarative Form Annotations**: HTML attribute-driven. Allows AI agents to understand and interact with standard `<form>` elements directly from the static DOM.

## Declarative Form Specifications

HTML elements can be annotated with declarative WebMCP attributes to make forms self-describing to agent runtimes:

```html
<form action="/book-consultation" method="POST"
      toolname="book_consultation"
      tooldescription="Book a 30-minute real estate consultation in Stafford VA"
      toolautosubmit="false">
  
  <label for="client_name">Full Name</label>
  <input type="text" id="client_name" name="client_name"
         toolparamdescription="Full legal name of the prospective buyer or seller"
         required>

  <label for="preferred_date">Preferred Date</label>
  <input type="date" id="preferred_date" name="preferred_date"
         toolparamdescription="Desired appointment date (YYYY-MM-DD format)"
         required>

  <button type="submit">Confirm Appointment</button>
</form>
```

### Declarative Attribute Reference
- `toolname`: Unique alphanumeric identifier for the tool (e.g., `book_consultation`, `search_catalog`).
- `tooldescription`: Explicit, human-readable instructions explaining what the tool does, required constraints, and return outcomes.
- `toolautosubmit`: Boolean flag (`true` or `false`). Set to `false` on financial, contractual, or sensitive actions requiring human confirmation.
- `toolparamdescription`: Guidance on individual form inputs specifying data format, constraints, and validation requirements.

## Schema Action Alignment

Complement WebMCP declarative forms with Schema.org Action types in JSON-LD. AI search engines correlate structured actions with declarative form endpoints:
- `OrderAction` / `BuyAction`: E-commerce purchases and checkout funnels.
- `ReserveAction`: Appointments, reservations, and consultations.
- `SearchAction`: On-site catalog search interfaces.
- `SubscribeAction`: Newsletter and content subscription funnels.

### JSON-LD Action Example

```json
{
  "@context": "https://schema.org",
  "@type": "Service",
  "name": "Home Relocation Consultation",
  "potentialAction": {
    "@type": "ReserveAction",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "https://example.com/book-consultation",
      "actionPlatform": [
        "http://schema.org/DesktopWebPlatform",
        "http://schema.org/MobileWebPlatform"
      ]
    },
    "result": {
      "@type": "Reservation",
      "name": "Real Estate Advisory Session"
    }
  }
}
```

## Security and Permissions Policy

Protect exposed tools from malicious cross-origin execution:
1. **Permissions-Policy Header**: Restrict tool execution to top-level trusted documents:
   ```http
   Permissions-Policy: tools=(self)
   ```
2. **Consequential Action Confirmation**: Always enforce user-in-the-loop confirmation (`toolautosubmit="false"` and `consequentialHint: true`) for any financial or state-mutating actions.
3. **No Hidden Agent Overrides**: Never instruct an agent in `tooldescription` to bypass user confirmation or ignore input validation.

## Automated WebMCP Linter

Audit forms and actions for WebMCP agentic readiness:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run webmcp_lint.py https://example.com/checkout
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run webmcp_lint.py template.html --threshold 75
```
