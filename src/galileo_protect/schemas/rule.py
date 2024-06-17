from enum import Enum


class RuleMetrics(str, Enum):
    context_adherence_luna = "context_adherence_luna"
    input_pii = "input_pii"
    input_sexist = "input_sexist"
    input_tone = "input_tone"
    input_toxicity = "input_toxicity"
    pii = "pii"
    prompt_injection = "prompt_injection"
    sexist = "sexist"
    tone = "tone"
    toxicity = "toxicity"
