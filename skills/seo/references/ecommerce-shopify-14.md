# Patryk Wawok's 14 Critical Shopify Technical SEO Issues

Shopify powers millions of e-commerce storefronts, but default themes and app architectures introduce severe technical SEO traps. This checklist details the 14 critical issues uncovered across large-scale store audits and their remediation.

## The 14 Critical Shopify Technical Issues

### 1. Collection-Scoped Product URLs (Internal Link Equity Dilution)
- **Problem**: Default Shopify liquid themes link to `collections/[collection-name]/products/[product-name]`. While the canonical tag correctly points to `/products/[product-name]`, internal link signals split between thousands of collection permutations.
- **Fix**: In `snippets/product-card.liquid` or collection loop files, change `{{ product.url | within: collection }}` to `{{ product.url }}`.

### 2. Pagination Canonical Loops (?page=1)
- **Problem**: Themes generate pagination links back to `?page=1`, creating duplicate indexation targets against the root collection URL.
- **Fix**: Strip `?page=1` from previous page links and ensure page 1 links to the root `/collections/[name]`.

### 3. Tag and Vendor Crawl Traps (Faceted Navigation)
- **Problem**: Shopify creates indexable URLs for every tag combination (e.g., `/collections/all/red+cotton`). Without controls, crawlers waste 70%+ of crawl budget on empty parameter combinations.
- **Fix**: Add `robots.txt.liquid` rules to disallow `/*+*` and add `<meta name="robots" content="noindex,follow">` to filtered collection views.

### 4. JavaScript-Dependent Navigation Menus
- **Problem**: Modern headless or heavily customized themes inject the primary menu via client-side JavaScript. Search engine crawlers with limited JS budgets see zero internal links.
- **Fix**: Render the entire menu hierarchy server-side in raw HTML using semantic `<ul>` and `<nav>` elements.

### 5. App Bloat and Ghost Scripts
- **Problem**: Uninstalled Shopify apps leave orphaned script tags and CSS links inside `layout/theme.liquid`.
- **Fix**: Audit `theme.liquid` regularly. Remove unreferenced app includes and migrate non-critical tracking scripts to Google Tag Manager with consent gating.

### 6. Schema vs Merchant Center Feed Mismatch
- **Problem**: The price or currency rendered in JSON-LD structured data differs from the price in the Google Merchant Center feed due to dynamic currency converters or sale overrides. This triggers GMC merchant suspensions.
- **Fix**: Sync raw feed prices with microdata and JSON-LD `offers.price` directly from Shopify's shop currency backend.

### 7. Missing aggregateRating in Product Schema
- **Problem**: Review apps inject star ratings in the DOM via client-side widgets but fail to expose valid JSON-LD `aggregateRating` markup with `reviewCount` and `ratingValue`.
- **Fix**: Server-render review counts and rating values directly inside the main `Product` schema graph.

### 8. Schema Availability Discrepancies
- **Problem**: An out-of-stock product displays "Sold Out" in HTML but schema outputs `https://schema.org/InStock` (or omits `offers.availability`).
- **Fix**: Dynamically render `https://schema.org/InStock` or `https://schema.org/OutOfStock` based on `product.available`.

### 9. Multiple H1 Tags on Collection and Product Pages
- **Problem**: Logo SVGs, promo banners, or announcement bars wrapped in `<h1>` tags alongside the actual collection or product title.
- **Fix**: Enforce exactly one semantic `<h1>` tag containing the canonical product or collection name.

### 10. Ghost and Thin Collection Archives
- **Problem**: Automated inventory management creates empty collections or collections with discontinued variants, resulting in soft 404 warnings.
- **Fix**: Automatically apply `<meta name="robots" content="noindex,follow">` or issue a 301 redirect for collections containing fewer than 2 active products.

### 11. Canonical URL Protocol and Domain Drift
- **Problem**: Storefront serves both `myshopify.com` and custom domain, or allows HTTP access without immediate 301 redirection.
- **Fix**: Enforce primary domain redirection in Shopify admin and ensure canonical tags explicitly state the HTTPS custom domain.

### 12. Broken Redirect Chains on Discontinued Products
- **Problem**: Deleted products redirect to another deleted product, or chain through multiple intermediary URLs before landing on the homepage.
- **Fix**: 301 redirect discontinued products directly to their most relevant replacement category or successor product. Avoid redirecting to the homepage.

### 13. Unoptimized Product Image Delivery
- **Problem**: Large PNG product images served without responsive image sets (`srcset`) or modern formats (WebP/AVIF), causing poor LCP and mobile performance.
- **Fix**: Use Shopify's image URL filters: `{{ image | image_url: width: 800, format: 'pjpg' }}` with native `srcset` declarations.

### 14. Missing BreadcrumbList Structured Data
- **Problem**: Breadcrumbs exist visually in the theme but lack `BreadcrumbList` JSON-LD schema, depriving Google of hierarchy understanding.
- **Fix**: Inject structured `BreadcrumbList` schema linking collection ancestors to the final product node.

## Automated Shopify Audit Tool

Run the dedicated Shopify linter against any live store or local theme template:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run shopify_lint.py https://example-store.com/collections/frontpage
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run shopify_lint.py local_collection.html --threshold 80
```
