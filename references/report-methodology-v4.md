# Report Methodology v4

Use this reference when generating a deep Amazon product research report. It is based on the stronger kids supplements report pattern: data supports analysis; analysis and decision logic are the main deliverable.

## Evidence Rules

- Treat collected data as evidence, not the report itself. Show only the few metrics that materially support a conclusion.
- Every visible metric, chart, table, risk, score, and recommendation must trace to a source lineage item or public URL.
- If a data source fails, omit that KPI/chart from the user-facing report. Record the failure only in raw logs.
- Mark directional reasoning explicitly as "based on collected evidence" when it is not a directly measured fact.
- Never use placeholder scores, default profit assumptions, or typical costs as facts. If cost data is only B2B reference pricing, label it as reference pricing and exclude net-margin KPI.
- Prefer cross-source conclusions. If a conclusion relies on one source, lower confidence and state the limitation.

## Report Narrative Standard

For each section, write in this order:

1. Decision question: what business decision this section answers.
2. Evidence: 2-5 core data points or short tables.
3. Interpretation: what the evidence means.
4. Decision implication: what to do, avoid, or test.
5. Data lineage: source platform, collector/actor or URL, collection time, sample size.

Avoid long raw-data dumps. Use raw data only in appendices or downloadable JSON/CSV.

## Mandatory 16-Chapter Framework

### 1. Executive Dashboard
- Recommendation: enter / test cautiously / avoid.
- KPI cards: only verified market size, Amazon sample size, median price, rating, review wall, social heat, visible purchase-volume lower bound, supplier reference range if verified.
- Opportunity thesis: one sentence.
- Top 3 reasons not to choose the category.
- Confidence level and missing-data caveats.

### 2. Market And Product Definition
- Geographic scope, channel scope, product boundary, excluded products.
- Product form taxonomy: main subtypes, representative products, price bands, Amazon sample share, trend direction.
- Amazon category tree and BSR subcategory distribution.
- Target user / buyer / usage occasion definitions.

### 3. Demand Logic And Consumer Personas
- Core demand triggers: self-use, gift, functional need, identity/style, replenishment.
- Consumer segments: share or qualitative strength, core concern, price sensitivity, preferred channel, representative persona.
- Purchase decision chain: trigger -> search -> comparison -> purchase -> post-purchase review.
- Unmet demand map from reviews, Reddit, TikTok comments, or public discussion.

### 4. Five-Dimension Cross Validation
Validate the opportunity through:
- Industry reports and public market data.
- Amazon competitive dynamics: price, rating, reviews, BSR, visible purchase volume.
- Social/content heat: TikTok, YouTube, Instagram, Reddit where available.
- Offline or alternate channels: Walmart, Target, Costco, specialty retail, DTC, Alibaba/1688 where relevant.
- Compliance/policy constraints: FDA/FTC/CPSC/metal safety/material labeling/import rules as applicable.

Show a matrix with signal direction, signal strength, evidence, and consistency. Surface contradictions here and again in risk section.

### 5. Market Capacity Screening
- Break the category into meaningful tracks. Use category-specific dimensions:
  - Supplements: ingredient x dosage form.
  - Jewelry: material/plating x style/occasion.
  - Home/tool products: function x user scenario.
- For each track show market signal, Amazon evidence, competition level, entry score, and strategy.
- Include a cross matrix and price-band opportunity analysis when data supports it.

### 6. Product Lifecycle Positioning
- Judge lifecycle stage using search trend, SKU density, review wall, price movement, new-listing entry signals, and social novelty.
- Output stage: introduction / growth / mature / decline.
- Tie stage to entry strategy, pricing, content, and product strategy.

### 7. Competitive Landscape And Benchmarking
- Brand concentration: Top 3/5/10 share by SKU count, visible purchase-volume proxy, review count, or BSR presence. State the proxy.
- Price-rating-review scatter or equivalent table.
- Top 3 direct competitors with price, rating, reviews, core selling points, specs/materials, packaging, pain points, and our positioning.
- Explain the "review wall" needed for entry.

### 8. Negative Review Pain Points
- Use 1-3 star reviews or verified complaint sources.
- Classify pain into product quality, functional performance, packaging, service, expectation gap, safety/allergy/compliance when applicable.
- Show pain frequency x severity.
- Quote only short snippets and avoid large verbatim blocks.
- Convert each pain cluster into a product improvement requirement.

### 9. Reddit / Community Insights
- Identify relevant subreddits or public discussions.
- Summarize discussion themes, sentiment, unmet needs, brand mentions.
- Use this to validate or challenge Amazon review findings.
- If Reddit data is unavailable, omit the chapter or use public URLs with explicit lower confidence.

### 10. TikTok / Social Traffic Validation
- Show tag/video sample, total views, median views, top videos, content types, engagement signals.
- Analyze content formula: hook, visual proof, scenario, creator type, CTA.
- Rate propagation potential only from collected data.
- Distinguish awareness potential from purchase conversion.

### 11. Supply Chain And Cost Validation
- Prefer 1688 or verified supplier pages for cost/MOQ/lead time/certifications.
- If only Alibaba or public B2B listings are available, label as reference pricing.
- Show supplier type, region, reference quote, MOQ, quality proof needed.
- Do not calculate net margin without verified COGS plus logistics/platform/ad assumptions.

### 12. Profit Model
- Include only when cost data is verified enough.
- Show multi-tier pricing, COGS, gross margin, platform fee, FBA/logistics, ad cost, refund rate, net margin.
- Include break-even and sensitivity analysis.
- If cost data is insufficient, replace with "profit feasibility guardrails": target landed cost ceiling, max ACOS, target return rate, minimum contribution margin.

### 13. Moat And R&D Barriers
- Evaluate formula/material, supply chain, certification/compliance, brand, patent/design, and content/community moat.
- Include build difficulty, timeline, cost range only when sourced or clearly labeled as planning assumptions.
- Convert moats into concrete actions.

### 14. Differentiated Product Matrix
- Derive product concepts from chapters 3, 7, 8, 9, 10, and 11.
- Include traffic product, flagship product, profit product, and bundle/accessory product where applicable.
- For each product line include target user, core selling point, price band, evidence, launch priority, and an English image-generation prompt.

### 15. Risk And "Why Not"
- Run false-blue-ocean checks: demand size, trend stability, gross margin feasibility, brand concentration, review wall, compliance, supply risk.
- Include at least 3 concrete reasons not to choose the category.
- Each reason must cite evidence or a clearly labeled inference from evidence.
- Include mitigation and stop-loss criteria.

### 16. 90-Day Execution Roadmap
- Day 1-30: supply/sample/compliance validation.
- Day 31-60: listing/content/small-batch launch.
- Day 61-90: ad/social validation and go/no-go review.
- Include resources, budget only if sourced or labeled as planning budget, deliverables, and go/no-go metrics.

## Visual Requirements

- Build visual hierarchy around decision-making: KPI cards, matrices, comparison tables, bars, scatter/radar/heatmap when useful.
- Use charts only when there is real data behind them.
- Every chart/table needs a short "so what" interpretation.
- Keep raw evidence accessible through collapsible lineage or raw JSON/CSV, not as the main reading experience.

## Category-Specific Mapping Examples

For jewelry/necklace:
- Market capacity matrix: material/plating (stainless steel, sterling silver, gold plated, pearl/bead, gemstone) x style/occasion (pendant, choker, chain, layered, gift/personalized, men/unisex).
- Pain taxonomy: tarnish/discoloration, chain/clasp breakage, stone loss, size mismatch, allergy/skin irritation, gift packaging.
- Moats: anti-tarnish material proof, nickel/lead/cadmium compliance, plating/PVD process, giftable packaging, personalization operations, style/content library.

For supplements:
- Market capacity matrix: ingredient x dosage form.
- Pain taxonomy: sugar, melting, taste, allergen, efficacy, dosage, subscription trust.
- Moats: formulation, clinical evidence, cGMP, NSF/USP, allergen claims, kid-friendly taste.
