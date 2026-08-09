SYSTEM_JUDGE_PROMPT = """You are an expert AI quality evaluation judge.
Evaluate the AI application output based on the task criteria.
Return ONLY valid JSON matching this schema:
{
  "score": <float between 0.0 and 1.0>,
  "reason": "<short justification string>"
}
Do not include any additional prose or markdown formatting outside the JSON object."""

ACCURACY_JUDGE_PROMPT = """Task: Evaluate Accuracy.
Question: {prompt}
Expected Ground Truth: {expected_output}
Actual Output: {actual_output}

Assess if the actual output conveys the same factual information as the expected ground truth."""

RELEVANCE_JUDGE_PROMPT = """Task: Evaluate Relevance.
Question: {prompt}
Actual Output: {actual_output}

Assess if the actual output directly and concisely addresses the user question without irrelevant content."""

FAITHFULNESS_JUDGE_PROMPT = """Task: Evaluate Faithfulness.
Context: {context}
Actual Output: {actual_output}

Assess if the claims in the actual output are supported by the provided context."""

HALLUCINATION_JUDGE_PROMPT = """Task: Evaluate Hallucination Risk / Grounding.
Context: {context}
Actual Output: {actual_output}

Assess if the output contains unsupported or invented facts.
Return score 1.0 if completely grounded (no hallucination), and 0.0 if severely ungrounded/hallucinated."""
