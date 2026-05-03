# Edge Case: Ambiguous Scheme Name

## Trigger
User asks using partial or ambiguous name (example: "Tell me expense ratio of HDFC fund").

## Risk
Wrong scheme retrieval and wrong fact delivery.

## Expected Handling
- LLM-assisted entity extractor identifies multiple candidate schemes.
- Assistant asks one clarifying factual question before answering.
- No assumptions about scheme identity.

## Validation
- Final answer is generated only after scheme is disambiguated.
- Answer still follows 3-sentence and one-citation rules.
