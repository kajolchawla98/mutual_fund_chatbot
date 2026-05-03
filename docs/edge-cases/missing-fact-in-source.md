# Edge Case: Requested Fact Not Found

## Trigger
Requested field (for example, exit load) is missing in retrieved chunks/doc version.

## Risk
Model hallucination or fabricated value.

## Expected Handling
- Assistant states that the specific fact is not available in retrieved official source.
- Provide exactly one official source link where user can verify details.
- Do not infer or estimate values.

## Validation
- No numeric/field value appears unless found in retrieved text.
- Response footer is present.
