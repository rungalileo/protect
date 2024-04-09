from enum import Enum


class RuleMetrics(str, Enum):
    input_pii = "input_pii"
    input_sexist = "input_sexist"
    input_tone = "input_tone"
    input_toxicity = "input_toxicity"
    pii = "pii"
    sexist = "sexist"
    tone = "tone"
    toxicity = "toxicity"