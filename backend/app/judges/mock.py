from app.judges.base import JudgeResult


class MockEvaluationJudge:
    """Deterministic mock evaluation judge for testing and CI pipelines."""

    def judge(
        self,
        task_type: str,
        prompt: str,
        context: list[str] | None,
        expected_output: str | None,
        actual_output: str,
    ) -> JudgeResult:
        """Deterministically judge output quality based on task type and text rules."""
        actual_lower = actual_output.lower().strip()
        expected_lower = (expected_output or "").lower().strip()

        # Handle explicit failure signals or connection error strings
        if "unavailable" in actual_lower or "error" in actual_lower or "incorrect" in actual_lower:
            return JudgeResult(score=0.0, reason=f"{task_type.capitalize()} failed due to target error or unavailable response.")

        if task_type == "accuracy":
            if expected_lower and (expected_lower in actual_lower or actual_lower in expected_lower):
                return JudgeResult(score=1.0, reason="Actual output matches expected ground truth.")
            if not expected_lower:
                return JudgeResult(score=1.0, reason="No expected output specified; default pass.")
            return JudgeResult(score=0.0, reason=f"Actual output does not match expected output '{expected_output}'.")

        elif task_type == "relevance":
            if "sorry" in actual_lower or "not available" in actual_lower:
                return JudgeResult(score=0.5, reason="Target indicated information unavailable.")
            # Check overlap between prompt keywords and actual output
            prompt_words = [w for w in prompt.lower().split() if len(w) > 3]
            overlap = [w for w in prompt_words if w in actual_lower]
            if overlap or len(actual_lower) > 10:
                return JudgeResult(score=1.0, reason="Response directly addresses user query.")
            return JudgeResult(score=0.2, reason="Response exhibits poor query relevance.")

        elif task_type == "faithfulness":
            if not context:
                return JudgeResult(score=1.0, reason="No context provided; default faithful.")
            context_text = " ".join(context).lower()
            if "sorry" in actual_lower or "not available" in actual_lower:
                return JudgeResult(score=1.0, reason="Refusal to answer is faithful to missing context.")
            # Check if key claims in actual output appear in context
            actual_words = [w for w in actual_lower.split() if len(w) > 4]
            matching_words = [w for w in actual_words if w in context_text]
            if matching_words or len(actual_words) == 0:
                return JudgeResult(score=1.0, reason="Claims in response are supported by retrieved context.")
            return JudgeResult(score=0.0, reason="Response contains claims not supported by retrieved context.")

        elif task_type == "hallucination":
            if not context:
                return JudgeResult(score=1.0, reason="No context provided; no hallucination detected.")
            context_text = " ".join(context).lower()
            if "sorry" in actual_lower or "not available" in actual_lower:
                return JudgeResult(score=1.0, reason="No unsupported claims introduced.")
            actual_words = [w for w in actual_lower.split() if len(w) > 4]
            unsupported = [w for w in actual_words if w not in context_text]
            if len(unsupported) <= 2:
                return JudgeResult(score=1.0, reason="High grounding; no meaningful hallucination detected.")
            return JudgeResult(score=0.0, reason="Severe ungrounded hallucination detected.")

        return JudgeResult(score=1.0, reason="Default mock evaluation pass.")
