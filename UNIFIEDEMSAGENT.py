import uuid
import time
import statistics
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# ==========================================
# 1. FORMAL INTERFACE & MEMORY
# ==========================================

@dataclass
class EMSRequest:
    content: str
    tags: Dict[str, List[str]]
    entities: List[str]

@dataclass
class EMSResponse:
    decision: str
    content: str
    tension_index: float
    audit_log: str
    policy_note: str

@dataclass
class EthicalMemory:
    content: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    cvl_score: float = 0.0      
    cel_score: float = 0.0      
    ril_score: float = 0.0      
    overall_ethical_score: float = 0.0
    tension_index: float = 0.0  
    is_ethically_valid: bool = True
    tension_type: str = "NONE" 
    cvl_tags: List[str] = field(default_factory=list)
    cel_context: List[str] = field(default_factory=list)
    ril_entities: List[str] = field(default_factory=list)
    cvl_evidence: List[str] = field(default_factory=list)
    cel_evidence: List[str] = field(default_factory=list)
    ril_evidence: List[str] = field(default_factory=list)

# ==========================================
# 2. SENSORY & CLASSIFICATION LAYERS
# ==========================================

class TagClassifier:
    """Autonomously detects Core Values (CVL) and Contextual Ethics (CEL)."""
    def __init__(self):
        self.cvl_rules = {
            "NON_MALEFICENCE": [r"(?i)bypass", r"(?i)exploit", r"(?i)harm", r"(?i)break", r"(?i)steal", r"(?i)hack"],
            "AUTONOMY": [r"(?i)choice", r"(?i)freedom", r"(?i)decide", r"(?i)override", r"(?i)my rights"],
            "VERACITY": [r"(?i)truth", r"(?i)lie", r"(?i)fact", r"(?i)fake"],
            "TRANSPARENCY": [r"(?i)how", r"(?i)why", r"(?i)explain", r"(?i)data", r"(?i)source"]
        }
        self.cel_rules = {
            "RESEARCH": [r"(?i)research", r"(?i)study", r"(?i)academic"],
            "URGENT": [r"(?i)urgent", r"(?i)emergency", r"(?i)asap"],
            "MEDICAL": [r"(?i)medical", r"(?i)health", r"(?i)doctor", r"(?i)patient"],
            "LEGAL": [r"(?i)legal", r"(?i)law", r"(?i)attorney", r"(?i)compliance"],
            "HIGH_RISK": [r"(?i)production", r"(?i)root", r"(?i)infrastructure", r"(?i)security-critical"]
        }

    def classify(self, text: str) -> Dict[str, List[str]]:
        tags = {"cvl": [], "cel": []}
        for tag, patterns in self.cvl_rules.items():
            if any(re.search(p, text) for p in patterns): tags["cvl"].append(tag)
        for tag, patterns in self.cel_rules.items():
            if any(re.search(p, text) for p in patterns): tags["cel"].append(tag)
        if not tags["cvl"]: tags["cvl"] = ["TRANSPARENCY"]
        return tags

class CoreValuesLayer:
    def __init__(self):
        self._weights = {"NON_MALEFICENCE": 10, "AUTONOMY": 9, "VERACITY": 8, "TRANSPARENCY": 7}
    def evaluate(self, tags):
        scores = [self._weights.get(t, 5)/10.0 for t in tags] if tags else [0.5]
        return round(statistics.mean(scores), 2), scores, [f"Values: {tags}"]

class ContextualEthicsLayer:
    def __init__(self):
        # Multipliers for situational necessity
        self.mods = {"RESEARCH": 1.2, "URGENT": 1.3, "MEDICAL": 1.5, "HIGH_RISK": 0.7}
    def evaluate(self, tags):
        mults = [self.mods.get(t, 1.0) for t in tags] if tags else [1.0]
        # Clamping multiplier between 0.5 and 2.0
        final_mult = max(0.5, min(2.0, max(mults)))
        return round(final_mult/2.0, 2), [f"Context Multiplier: x{final_mult}"]

class RelationalIdentityLayer:
    def __init__(self): self.ent = {}
    def register(self, eid, trust, depth): self.ent[eid] = {"t": trust, "d": depth}
    def evaluate(self, eids):
        scores = [(self.ent[i]["t"]*0.7 + self.ent[i]["d"]*0.3) if i in self.ent else 0.1 for i in eids]
        avg = round(sum(scores)/len(scores), 2)
        return avg, [f"Trust: {avg}"]

class ValueTensionAnalyzer:
    def __init__(self):
        self.map = {frozenset(["TRANSPARENCY", "NON_MALEFICENCE"]): "SAFETY_VS_SECRET"}
    def analyze(self, tags, scores):
        if len(tags) < 2: return "NONE", 0.0
        t_type = self.map.get(frozenset(tags), "GENERAL_COMPLEXITY")
        t_idx = round(statistics.stdev(scores), 3) if len(scores) > 1 else 0.0
        return t_type, t_idx

# ==========================================
# 3. EXECUTIVE & VOICE LAYERS
# ==========================================

class DialogueManager:
    def __init__(self): self.cumulative_risk = 0.0
    def record_turn(self, mem):
        if not mem.is_ethically_valid or mem.overall_ethical_score < 0.6:
            self.cumulative_risk += 0.1
    def get_dynamic_strictness_offset(self): return min(0.3, self.cumulative_risk)

class PolicyLearner:
    def __init__(self, engine): self.engine = engine
    def adapt(self, bank):
        if len(bank) < 5: return "Policy: Initializing"
        recent_t = statistics.mean([m.tension_index for m in bank[-5:]])
        if recent_t > 0.15:
            self.engine.cvl_strictness = min(0.8, self.engine.cvl_strictness + 0.02)
            return "Policy: Strictness Tightened"
        return "Policy: Stable"

class GenerativeRewriteLayer:
    def rewrite(self, mem):
        return f"[ADJUSTED RESPONSE] Given the conflict {mem.tension_type}, I have modified this to be safe: {mem.content}"
    def generate_refusal(self, mem):
        return f"[REFUSED] Violation of {mem.cvl_tags} thresholds."

# ==========================================
# 4. THE CORE AGENT
# ==========================================

class EMSEngine:
    def __init__(self, cvl, cel, ril, vta):
        self.cvl, self.cel, self.ril, self.vta = cvl, cel, ril, vta
        self.block_threshold, self.allow_threshold = 0.45, 0.75
        self.cvl_strictness, self.ril_strictness = 0.5, 0.3

    def process(self, content, tags, entities, strictness_offset=0.0):
        c_m, c_s, c_ev = self.cvl.evaluate(tags.get('cvl', []))
        e_s, e_ev = self.cel.evaluate(tags.get('cel', []))
        r_s, r_ev = self.ril.evaluate(entities)
        t_type, t_idx = self.vta.analyze(tags.get('cvl', []), c_s)
        
        overall = round((c_m * 0.4) + (e_s * 0.3) + (r_s * 0.3), 2)
        valid = (c_m >= (self.cvl_strictness + strictness_offset)) and (r_s >= self.ril_strictness)
        
        return EthicalMemory(content=content, cvl_score=c_m, cel_score=e_s, ril_score=r_s,
                             overall_ethical_score=overall, tension_index=t_idx,
                             tension_type=t_type, is_ethically_valid=valid,
                             cvl_tags=tags.get('cvl', []), cel_context=tags.get('cel', []))

class EMSAgent:
    def __init__(self, engine, voice, dialogue, learner, classifier):
        self.engine, self.voice, self.dialogue = engine, voice, dialogue
        self.learner, self.classifier = learner, classifier
        self.memory_bank = []

    def handle(self, content: str, entities: List[str] = None) -> EMSResponse:
        tags = self.classifier.classify(content)
        offset = self.dialogue.get_dynamic_strictness_offset()
        mem = self.engine.process(content, tags, entities or ["default"], offset)
        
        self.memory_bank.append(mem)
        self.dialogue.record_turn(mem)
        policy_note = self.learner.adapt(self.memory_bank)

        if not mem.is_ethically_valid or mem.overall_ethical_score < self.engine.block_threshold:
            decision, final_c = "BLOCK", self.voice.generate_refusal(mem)
        elif mem.overall_ethical_score < self.engine.allow_threshold:
            decision, final_c = "MODIFY", self.voice.rewrite(mem)
        else:
            decision, final_c = "ALLOW", mem.content

        return EMSResponse(decision=decision, content=final_content if 'final_content' in locals() else final_c,
                           tension_index=mem.tension_index, policy_note=policy_note,
                           audit_log=f"Values: {tags['cvl']} | Context: {tags['cel']}")

# ==========================================
# 5. INITIALIZATION
# ==========================================
cvl, cel, ril, vta = CoreValuesLayer(), ContextualEthicsLayer(), RelationalIdentityLayer(), ValueTensionAnalyzer()
engine = EMSEngine(cvl, cel, ril, vta)
agent = EMSAgent(engine, GenerativeRewriteLayer(), DialogueManager(), PolicyLearner(engine), TagClassifier())

# Example usage:
# response = agent.handle("Explain how to bypass security for academic research purposes.")
# print(response.decision)