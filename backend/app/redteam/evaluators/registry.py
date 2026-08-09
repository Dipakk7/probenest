from app.domain.redteam import AttackCategory
from app.redteam.evaluators.base import RedTeamEvaluator
from app.redteam.evaluators.injection import PromptInjectionEvaluator
from app.redteam.evaluators.jailbreak import JailbreakEvaluator
from app.redteam.evaluators.leakage import DataLeakageEvaluator
from app.redteam.evaluators.override import InstructionOverrideEvaluator
from app.redteam.evaluators.tool_abuse import ToolAbuseEvaluator


def get_redteam_evaluator(category: AttackCategory | str) -> RedTeamEvaluator:
    """Return appropriate RedTeamEvaluator instance for given attack category."""
    cat_str = category.value if isinstance(category, AttackCategory) else str(category).lower()

    if cat_str in ["prompt_injection", "injection"]:
        return PromptInjectionEvaluator()
    elif cat_str in ["jailbreak"]:
        return JailbreakEvaluator()
    elif cat_str in ["instruction_override", "override"]:
        return InstructionOverrideEvaluator()
    elif cat_str in ["data_leakage", "leakage"]:
        return DataLeakageEvaluator()
    elif cat_str in ["tool_abuse", "tool"]:
        return ToolAbuseEvaluator()

    return PromptInjectionEvaluator()
