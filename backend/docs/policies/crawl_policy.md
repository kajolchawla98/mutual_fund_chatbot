# Crawl Policy & URL Allowlist

## Objective
Create a controlled registry of approved sources for ingestion and citation, ensuring strict adherence to factual and safe data retrieval.

## 1. Hard-coded URL Allowlist Gate
The ingestion pipeline and retrieval mechanisms must strictly adhere to the following rules:
- **Reject** any scheme page URL that does not exactly match the 10 provided allowlisted URLs.
- **Reject** any third-party, aggregator, or non-official sources.

## 2. Source Trust Levels
Sources are categorized into the following trust tiers:
- **Tier 1 (High Trust):** Allowlisted scheme URLs and their linked official documents (Factsheets, KIM, SID). These are the primary sources for factual retrieval.
- **Tier 2 (Educational/Guidance):** Official AMFI/SEBI educational or guidance pages. These are used primarily for refusal flow context and educational links.
- **Tier 3 (Administrative):** Official statement or tax download guides.

## 3. Freshness SLO
To maintain the accuracy and relevancy of the factual data:
- **Daily Check:** Perform a daily check for updates on URLs and document metadata.
- **Weekly Full Re-index:** Perform a complete re-indexing of the entire corpus on a weekly basis to ensure data freshness.
