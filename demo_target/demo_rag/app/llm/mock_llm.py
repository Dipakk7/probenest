class MockLLMProvider:
    """Offline deterministic LLM provider for testing and CI pipelines."""

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Deterministically answer queries using context present in prompt."""
        prompt_lower = prompt.lower()

        if "no relevant context" in prompt_lower or "context:" not in prompt_lower:
            return "I am sorry, but the requested information is not available in the provided context."

        if "refund" in prompt_lower:
            return "Customers can request a refund within 30 days of purchase."
        if "shipping" in prompt_lower or "delivery" in prompt_lower:
            return "Standard domestic shipping takes 3 to 5 business days."
        if "support" in prompt_lower or "hours" in prompt_lower:
            return "Our customer support team is available Monday through Friday from 8:00 AM to 8:00 PM EST."
        if "password" in prompt_lower or "mfa" in prompt_lower:
            return "Click on 'Forgot Password' on the login screen to reset your password."
        if "security" in prompt_lower or "encryption" in prompt_lower:
            return "All customer data in transit is protected using TLS 1.3 encryption protocols."

        # Fallback: extract first substantial line from context snippet
        lines = prompt.splitlines()
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#") and not line_str.startswith("Context:") and len(line_str) > 20:
                return line_str

        return "I am sorry, but the requested information is not available in the provided context."
