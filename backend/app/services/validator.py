import re
from datetime import datetime


class ResponseValidator:
    def __init__(self):
        # Matches markdown links like [text](url) — the correct format we expect
        self.md_link_pattern = re.compile(r'\[.+?\]\(https?://[^\s)]+\)')

    def count_sentences(self, text):
        """Count sentences in the answer body only (excluding footer)."""
        body = text.split("Last updated from sources:")[0].strip()
        # Remove markdown links before counting to avoid splitting on URLs with dots
        body_no_links = self.md_link_pattern.sub("LINK", body)
        # Split on sentence-ending punctuation followed by whitespace or end of string
        sentences = re.split(r'[.!?]+(?:\s+|$)', body_no_links)
        return len([s for s in sentences if s.strip()])

    def has_citation_link(self, text):
        """Check if response has at least one proper markdown citation link."""
        return bool(self.md_link_pattern.search(text))

    def has_footer(self, text):
        """Check if response has the freshness footer."""
        return "Last updated from sources:" in text

    def validate(self, response_text, original_url=None):
        """
        Validates the LLM response against output contract rules.
        Only fails if citation link is missing or footer is missing.
        Sentence count is advisory only (LLM sometimes needs 4 for clarity).
        """
        reasons = []

        # 1. Citation link check (critical, unless it's a 'not available' response)
        is_not_available = "Sorry I can't help with this particular topic" in response_text
        if not self.has_citation_link(response_text) and not is_not_available:
            reasons.append("Missing citation link.")

        # 2. Footer check (critical, unless it's a 'not available' response)
        is_not_available = "Sorry I can't help with this particular topic" in response_text
        if not self.has_footer(response_text) and not is_not_available:
            reasons.append("Missing freshness footer date.")

        # 3. Sentence count (advisory, log only — do not fail for this)
        sentence_count = self.count_sentences(response_text)
        if sentence_count > 5:
            reasons.append(f"Advisory: response is long ({sentence_count} sentences).")

        # Only hard-fail on citation or footer missing (unless it's a 'not available' response)
        hard_fail = not is_not_available and (not self.has_citation_link(response_text) or not self.has_footer(response_text))

        if hard_fail:
            return {
                "is_valid": False,
                "reasons": reasons,
                "final_text": self.get_safe_fallback(original_url)
            }

        return {
            "is_valid": True,
            "reasons": reasons,
            "final_text": response_text
        }

    def get_safe_fallback(self, url=None):
        """Returns a safe fallback if validation hard-fails."""
        return "Sorry I can't help with this particular topic"
