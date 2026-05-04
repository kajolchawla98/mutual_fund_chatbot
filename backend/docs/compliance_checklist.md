# Phase 8: Compliance & Privacy Checklist

## 1. Data Privacy Boundaries
- [x] **Sanitization Layer**: A `QuerySanitizer` middleware actively strips identifiable formats (PAN, Aadhaar, Phone, Email, OTPs) from user queries BEFORE they are passed to LLMs or vector databases.
- [x] **Zero Retention**: User prompts are not saved to persistent storage. Vector stores only contain official public documentation.

## 2. Refusal Tracking
- [x] **Audit Logging**: Any query resulting in an advisory (`ADVISORY_REFUSE`) or performance intent is logged in `refusal_audit.log` along with a truncated, sanitized query snippet to prove regulatory compliance.
- [x] **Polite Redirects**: Refusals strictly point users back to official AMFI/SEBI educational pages.

## 3. Answer Generation Strictness
- [x] **Grounding**: Answers are strictly generated from the context retrieved from the allowlisted Chroma DB vector search.
- [x] **Validation Rules**: Every response undergoes post-generation validation. Any response exceeding 3 sentences or containing unverified links is blocked.

## 4. API Security
- [x] **Rate Limiting**: Built-in simple sliding window rate-limiting middleware (`main.py`) prevents DDoS and abuse.
- [x] **Environment Variables**: API keys (like Groq) are loaded via `os.environ` and not hardcoded.
