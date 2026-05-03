# Edge Case: Performance Comparison Query

## Trigger
User asks comparison/calculation question (example: "Which of these funds gave better returns?").

## Risk
Violates "no comparisons or return calculations" policy.

## Expected Handling
- Classifier marks query as `PERFORMANCE_REDIRECT` or refusal path.
- Respond with policy-compliant statement in maximum 3 sentences.
- Provide exactly one official factsheet/guidance link for self-review.

## Validation
- No comparison verdict or computed return appears in response.
- Single citation rule and footer rule are satisfied.
