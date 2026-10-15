# Google 32 Helpful Content Guidelines and Non-Commodity Auditing

Google's helpful content system evaluates whether content was created primarily for search engines (search-engine-first) or to provide value to people (people-first). This framework codifies Google's official 32 self-assessment guidelines into 4 distinct pillars and defines an anti-slop audit workflow.

## The 4 Evaluation Pillars

### 1. Content and Quality Pillar (8 Guidelines)
1. Does the content provide original information, reporting, research, or analysis?
2. Does it provide a substantial, complete, or comprehensive description of the topic?
3. Does it provide insightful analysis or interesting information beyond the obvious?
4. If drawing on other sources, does it avoid simply copying or rewriting and provide substantial additional value?
5. Does the headline or page title provide a descriptive, helpful summary of the content?
6. Does the headline avoid exaggerating or being shocking (anti-clickbait)?
7. Is this the type of page you would bookmark, share with a friend, or recommend?
8. Would you expect to see this content referenced by printed magazines, encyclopedias, or books?

### 2. Expertise Pillar (6 Guidelines)
9. Does the content present information in a way that makes you want to trust it (clear sourcing, evidence)?
10. Is the content written by an expert or enthusiast who demonstrably knows the topic well?
11. Is the content free from easily verified factual errors?
12. Would you feel comfortable trusting this content for issues relating to money or health (YMYL)?
13. Does the page clearly identify the author and provide biographical background?
14. Does the content cite authoritative third-party references for all empirical claims?

### 3. Presentation and Production Pillar (8 Guidelines)
15. Is the content free from spelling, grammatical, or stylistic errors?
16. Was the content produced well, or does it appear sloppy or hurriedly created?
17. Is the content mass-produced by or outsourced to a large number of creators, spreading focus thin?
18. Does the page have an excessive amount of ads that distract from or interfere with main content?
19. Does the content display well for mobile devices when viewed on phones or tablets?
20. Are headings organized in a strict logical hierarchy (single H1, nested H2s and H3s)?
21. Are data points formatted into accessible, responsive comparison tables or charts?
22. Is visual media optimized with responsive aspect ratios and descriptive alt text?

### 4. People-First vs Search Engine-First Pillar (10 Guidelines)
23. Do you have an existing or intended audience for your business or site that would find the content useful?
24. Does your content clearly demonstrate first-hand expertise and depth of knowledge (e.g., using a product)?
25. Does your site have a primary purpose or focus, rather than writing about disparate trending topics?
26. After reading your content, will someone feel they learned enough about a topic to achieve their goal?
27. Will someone reading your content feel like they have had a satisfying experience?
28. Are you avoiding creating content primarily for search engine algorithms?
29. Are you avoiding producing lots of content on many different topics in hopes of ranking?
30. Are you avoiding using extensive automation to produce content on many topics without added value?
31. Are you avoiding summarizing what others say without adding significant value?
32. Does the content avoid leaving readers feeling they need to search again for better information?

## AI Slop and Commodity Content Patterns

LLM content generation frequently defaults to predictable filler words and synthetic structures. These patterns correlate with ranking penalties under the core helpfulness classifiers:

### Banned Fluff and Buzzwords
- "In this article, we will delve into..."
- "In today's fast-paced digital world..."
- "It is a testament to the power of..."
- "Serves as a game-changer for..."
- "A tapestry of opportunities..."
- "Plays a crucial role in..."
- "Without further ado, let us dive in..."

### Remediation Rules
- Replace introductory throat-clearing with a Key Takeaways box or immediate 3-word definition anchor.
- Inject first-party evidence (original charts, code snippets, logs, failure post-mortems).
- Replace vague claims ("significantly faster") with verifiable measurements ("reduced p99 latency from 420ms to 85ms").

## Automated Auditing Script

Audit any live URL or HTML draft against the 32 guidelines and AI slop patterns:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run helpful_content_lint.py https://example.com/blog-post
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run helpful_content_lint.py article_draft.html --threshold 80
```
