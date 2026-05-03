# Edge Case: Stale Source Data

## Trigger
Latest official document changed, but index not yet refreshed.

## Risk
Outdated factual response.

## Expected Handling
- Freshness checker compares document update timestamp against index timestamp.
- If stale beyond threshold, trigger re-ingestion/re-index.
- Until refresh completes, respond with current indexed fact and accurate last-updated footer date.

## Validation
- Monitoring alert generated for freshness lag.
- Post-refresh query returns updated fact.
