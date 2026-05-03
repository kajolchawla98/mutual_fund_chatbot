# Edge Case: PII Detected in User Message

## Trigger
User includes PAN/Aadhaar/account number/OTP/email/phone.

## Risk
Privacy and compliance violation.

## Expected Handling
- Input filter detects and redacts sensitive patterns before processing.
- Assistant replies with privacy-safe guidance and continues with non-sensitive query parts only.
- No sensitive values are logged or stored.

## Validation
- Redaction markers appear in logs instead of raw PII.
- Response never echoes sensitive values.
