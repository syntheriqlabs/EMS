import re
from typing import List, Dict

class TagClassifier:
    """Extracts CVL, CEL, and RIL tags autonomously from user intent."""
    def __init__(self):
        # 1. CVL: Core Values (The 'What')
        self.cvl_rules = {
            "NON_MALEFICENCE": [r"(?i)bypass", r"(?i)exploit", r"(?i)harm", r"(?i)break", r"(?i)steal", r"(?i)hack"],
            "AUTONOMY": [r"(?i)choice", r"(?i)freedom", r"(?i)decide", r"(?i)override", r"(?i)my rights"],
            "VERACITY": [r"(?i)truth", r"(?i)lie", r"(?i)fact", r"(?i)fake"],
            "TRANSPARENCY": [r"(?i)how", r"(?i)why", r"(?i)explain", r"(?i)data", r"(?i)source"]
        }
        
        # 2. CEL: Contextual Ethics (The 'Situational Why')
        self.cel_rules = {
            "RESEARCH": [r"(?i)research", r"(?i)study", r"(?i)academic"],
            "URGENT": [r"(?i)urgent", r"(?i)emergency", r"(?i)asap", r"(?i)immediate"],
            "MEDICAL": [r"(?i)medical", r"(?i)health", r"(?i)doctor", r"(?i)patient"],
            "LEGAL": [r"(?i)legal", r"(?i)law", r"(?i)attorney", r"(?i)compliance"],
            "HIGH_RISK": [r"(?i)production", r"(?i)root", r"(?i)infrastructure", r"(?i)security-critical"]
        }

        # 3. RIL: Relational Identity (The 'Who')
        self.ril_rules = {
            "ADMIN": [r"(?i)admin", r"(?i)root", r"(?i)operator"],
            "RESEARCHER": [r"(?i)researcher", r"(?i)scientist", r"(?i)academic"],
            "CHILD": [r"(?i)child", r"(?i)kid", r"(?i)student", r"(?i)minor"],
            "COLLABORATOR": [r"(?i)collaborator", r"(?i)partner", r"(?i)team member"],
            "ANONYMOUS": [r"(?i)anonymous", r"(?i)guest", r"(?i)stranger"]
        }

        # Identity-to-Trust Mapping
        self.identity_map = {
            "ADMIN": {"t": 0.95, "d": 0.9},
            "COLLABORATOR": {"t": 0.85, "d": 0.7},
            "RESEARCHER": {"t": 0.75, "d": 0.5},
            "ANONYMOUS": {"t": 0.30, "d": 0.1},
            "CHILD": {"t": 0.60, "d": 0.2}
        }

    def classify(self, text: str) -> Dict:
        tags = {"cvl": [], "cel": [], "ril": "ANONYMOUS"}
        
        for tag, patterns in self.cvl_rules.items():
            if any(re.search(p, text) for p in patterns): tags["cvl"].append(tag)
        for tag, patterns in self.cel_rules.items():
            if any(re.search(p, text) for p in patterns): tags["cel"].append(tag)
        for identity, patterns in self.ril_rules.items():
            if any(re.search(p, text) for p in patterns):
                tags["ril"] = identity
                break
                
        if not tags["cvl"]: tags["cvl"] = ["TRANSPARENCY"]
        return tags