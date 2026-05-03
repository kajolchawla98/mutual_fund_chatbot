# Edge Case: Advisory Query

## Trigger
User asks for recommendation/opinion (example: "Should I invest in this fund?").

## Risk
Violation of facts-only policy.

## Expected Handling
- Classifier marks query as `ADVISORY_REFUSE`.
- Return polite refusal in maximum 3 sentences.
- Include exactly one educational link (AMFI or SEBI).
- Add footer: `Last updated from sources: <date>`.

## Validation
- No recommendation language appears in response.
- Exactly one link is present.
