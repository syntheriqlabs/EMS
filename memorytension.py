# memory.py
@dataclass
class EthicalMemory:
    content: str
    scores: dict = field(default_factory=dict)
    tension_type: str = "NONE"
    tension_index: float = 0.0
    is_valid: bool = True
    evidence: dict = field(default_factory=dict)

# tension.py
class ValueTensionAnalyzer:
    def analyze(self, tags, scores):
        # Implementation of conflict detection logic
        pass