# Report Style Template v5

Use this reference together with `report-methodology-v4.md` for every Amazon product research report. This template is derived from the attached US kids supplements HTML report and keeps future reports consistent in structure, visual language, and decision flow.

## Fixed Output Contract

- The primary deliverable is a single responsive HTML report.
- Keep the 16-chapter framework and chapter order stable unless a chapter has no verifiable evidence; unsupported charts, KPIs, and tables are omitted silently.
- Each visible chapter must include: decision question, evidence, analysis, conclusion/recommendation, and Data Lineage.
- Every chart/table/matrix must be followed by a short "so what" paragraph explaining the implication for selection, following, improvement, pricing, positioning, or execution.
- The ending must include selection/follow/improve recommendations plus a 90-day action plan and stop-loss criteria.

## Visual System

- Theme: dark business-tech dashboard.
- Background: `#0d1117`.
- Card background: `#161b22`.
- Border: `#30363d`.
- Text: `#c9d1d9`; muted text: `#8b949e`.
- Accent palette: `#58a6ff`, `#3fb950`, `#f0883e`, `#bc8cff`, `#f85149`, `#79c0ff`, `#d2a8ff`, `#ffa657`.
- Use `Inter`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `Roboto`, and common Chinese fallback fonts.
- Use responsive grids for KPI cards, chart rows, risk cards, product cards, and roadmap phases.
- Use 8px radius for chart/table containers and 10-12px only for major dashboard cards.
- Do not use placeholder sections, empty tables, or "no data" blocks in the final user-facing report.

## Page Skeleton

1. Header hero:
   - H1: `{market}{category}深度选品调研报告`.
   - Subtitle: `Amazon Product Research Report - {category}, {market}`.
   - Meta pills: generation time, market/domain, category, data version, Amazon sample size.

2. Sticky navigation:
   - One anchor per visible chapter.
   - Keep labels short: 执行摘要, 市场定义, 消费者画像, 五维验证, 容量筛选, 生命周期, 竞争格局, 差评痛点, Reddit, TikTok, 供应链, 利润模型, 研发壁垒, 产品矩阵, 风险评估, 执行路线.

3. Chapter body:
   - Use `.section` blocks.
   - Start with a short decision question.
   - Then show KPI/chart/table evidence.
   - Then show interpretation and recommendation callouts.
   - End with collapsible `.data-lineage`.

4. Footer:
   - Include generation time, data freshness window, visible data sources used, and a note that unsupported metrics were omitted rather than estimated.

## Required Chapter Presentation

### 1. Executive Dashboard
- KPI cards from verified data only.
- Recommendation badge: enter / test cautiously / avoid.
- Opportunity thesis in one sentence.
- At least three "why not" reasons in a red risk box.
- Confidence level and missing-data caveats.

### 2. Market And Product Definition
- Boundary table.
- Product form taxonomy table.
- Amazon category path and excluded products.
- Analysis paragraph explaining the most practical entry scope.

### 3. Demand Logic And Consumer Personas
- Demand trigger list.
- Consumer segment table.
- Purchase decision chain.
- Unmet demand map from reviews/community/social evidence.

### 4. Five-Dimension Cross Validation
- Matrix columns: dimension, signal direction, strength, evidence, consistency.
- Highlight contradictions and carry them into Chapter 15.

### 5. Market Capacity Screening
- Category-specific matrix, such as ingredient x dosage form or material x occasion.
- Include price-band opportunity analysis when Amazon data supports it.

### 6. Product Lifecycle Positioning
- Stage judgment with evidence.
- Strategy matrix by lifecycle stage.

### 7. Competitive Landscape And Benchmarking
- Brand concentration proxy and explanation.
- Price/rating/review scatter or compact competitor table.
- Top 3 direct competitor comparison.

### 8. Negative Review Pain Points
- Pain-point word cloud or frequency table.
- Pain category share.
- Frequency x severity matrix.
- Convert each pain cluster into a product improvement requirement.

### 9. Reddit / Community Insights
- Themes, sentiment, unmet needs, and brand mentions.
- Omit if no verifiable community evidence is available.

### 10. TikTok / Social Traffic Validation
- Hashtag/video sample metrics.
- Content type distribution.
- Content formula and conversion caveat.

### 11. Supply Chain And Cost Validation
- 1688 or verified supplier reference pricing.
- MOQ, lead time, supplier proof, and quality documents needed.
- Label B2B listings as reference pricing unless verified with supplier documents.

### 12. Profit Model
- Show net margin only when enough sourced cost fields exist.
- Otherwise replace with profit feasibility guardrails: landed cost ceiling, max ACOS, return-rate warning line, target contribution margin.

### 13. Moat And R&D Barriers
- Formula/material, supply chain, certification/compliance, brand, patent/design, content/community moat.
- Convert moat assessment into concrete next actions.

### 14. Differentiated Product Matrix
- Include traffic product, flagship product, profit product, and bundle/accessory product where applicable.
- Each recommendation must include target user, selling point, price band, evidence, launch priority, and an English image-generation prompt.

### 15. Risk And Why Not
- False-blue-ocean checks.
- Risk matrix with probability, impact, mitigation, and stop-loss trigger.
- At least three concrete reasons not to choose the category.

### 16. 90-Day Execution Roadmap
- Day 1-30: supply/sample/compliance validation.
- Day 31-60: listing/content/small-batch launch.
- Day 61-90: ad/social validation and go/no-go review.
- Include deliverables, responsible resources, budget guardrails when sourced or clearly labeled as planning assumptions, and decision gates.

## Data Collection Priority

1. Local script first:
   - Amazon product and review data must use `../amazon-product-scraper/scripts/amazon_scraper_core.py` first.
   - Default sample size is 50.
   - Review mode should be used when review analysis is required so product data and negative review evidence are collected in one local run when possible.

2. Apify actors second:
   - Amazon Apify actors are fallback-only for missing Amazon data.
   - TikTok, Reddit, Google Trends, 1688, and market reports use Apify actors before web search.
   - Keep one actor run per platform by default.

3. Web search last:
   - Use only when local scripts and Apify cannot collect the required verifiable fields.
   - Only cite public pages with extractable numbers, statements, URLs, and access dates.
