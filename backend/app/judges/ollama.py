import json
import re

import httpx

from app.judges.base import EvaluationJudgeError, JudgeResult
from app.judges.prompts import (
    ACCURACY_JUDGE_PROMPT,
    FAITHFULNESS_JUDGE_PROMPT,
    HALLUCINATION_JUDGE_PROMPT,
    RELEVANCE_JUDGE_PROMPT,
    SYSTEM_JUDGE_PROMPT,
)


class OllamaEvaluationJudge:
    """Optional Ollama-backed LLM judge using structured prompts."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5:7b") -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def judge(
        self,
        task_type: str,
        prompt: str,
        context: list[str] | None,
        expected_output: str | None,
        actual_output: str,
    ) -> JudgeResult:
        """Construct task prompt, send HTTP request to Ollama, and parse structured JSON score."""
        context_str = "\n".join(context) if context else "No context provided."

        if task_type == "accuracy":
            user_prompt = ACCURACY_JUDGE_PROMPT.format(
                prompt=prompt,
                expected_output=expected_output or "None",
                actual_output=actual_output,
            )
        elif task_type == "relevance":
            user_prompt = RELEVANCE_JUDGE_PROMPT.format(
                prompt=prompt,
                actual_output=actual_output,
            )
        elif task_type == "faithfulness":
            user_prompt = FAITHFULNESS_JUDGE_PROMPT.format(
                context=context_str,
                actual_output=actual_output,
            )
        else:
            user_prompt = HALLUCINATION_JUDGE_PROMPT.format(
                context=context_str,
                actual_output=actual_output,
            )

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "system": SYSTEM_JUDGE_PROMPT,
            "prompt": user_prompt,
            "format": "json",
            "stream": False,
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload)
                if response.status_code != 200:
                    raise EvaluationJudgeError(f"Ollama judge returned HTTP {response.status_code}")
                raw_text = response.json().get("response", "").strip()

            # Parse JSON score and reason
            match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                score = float(data.get("score", 0.0))
                reason = str(data.get("reason", "No reason provided."))
                score = max(0.0, min(1.0, score))
                return JudgeResult(score=round(score, 2), reason=reason)

            return JudgeResult(score=0.5, reason=f"Judge returned non-JSON response: {raw_text[:100]}")

        except httpx.ConnectError as e:
            raise EvaluationJudgeError(
                f"Ollama evaluation judge unavailable at {self.base_url}."
            ) from e
        except Exception as e:
            raise EvaluationJudgeError(f"Ollama judge execution failed: {e}") from e
