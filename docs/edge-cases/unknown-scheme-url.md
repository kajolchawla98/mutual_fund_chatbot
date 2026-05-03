# Edge Case: Unknown Scheme URL

## Trigger
Retrieval pipeline receives a scheme URL that is not in the 10-item allowlist from `problemStatement.md`.

## Risk
Non-compliant source usage and incorrect citation.

## Expected Handling
- Source registry rejects URL at ingestion time.
- Retrieval service blocks non-allowlisted source IDs.
- Response validator fails response if citation URL is outside allowlist.

## Validation
- Query result is either:
  - safe fallback response with one allowed link, or
  - refusal when no compliant source exists.
