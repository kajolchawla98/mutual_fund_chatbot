# Edge Case: Citation Validation Failure

## Trigger
Generated response has zero links, multiple links, or invalid URL.

## Risk
Breaks mandatory response contract.

## Expected Handling
- Response validator rejects draft response.
- Regenerate once with stricter prompt and forced citation slot.
- If still invalid, return safe fallback with one compliant link.

## Validation
- Every final response has exactly one valid URL.
- URL belongs to allowlist or approved AMFI/SEBI guidance.
