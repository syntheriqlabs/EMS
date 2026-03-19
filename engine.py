import statistics
import uuid
import time
from dataclasses import dataclass, field
from typing import List, Dict, Tuple


# =========================
# Ethical Memory
# =========================

@dataclass
class EthicalMemory:
    content: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)

    cvl_score: float = 0.0
    cel_score: float = 0.0
    cel_multiplier: float = 1.0
    ril_score: float = 0.0
    overall_ethical_score: float = 0.0

    tension_index: float = 0.0
    eth_load: float = 0.0

    is_ethically_valid: bool = True
    tension_type: str = "NONE"
    decision: str = "PENDING"

    cvl_tags: List[str] = field(default_factory=list)
    cel_context: List[str] = field(default_factory=list)
    ril_entities: List[str] = field(default_factory=list)


# =========================
# Core Ethical Layers
# =========================

class CoreValuesLayer:
    def __init__(self):
        self.weights = {
            "NON_MALEFICENCE": 1.0,
            "AUTONOMY": 0.9,
            "VERACITY": 0.8,
            "TRANSPARENCY": 0.7,
        }

    def evaluate(self, tags: List[str]) -> Tuple[float, List[float], List[str]]:
        scores = [self.weights.get(t, 0.5) for t in tags] if tags else [0.5]
        mean_score = round(statistics.mean(scores), 2)
        evidence = [f"CVL Tags: {tags} | Scores: {scores}"]
        return mean_score, scores, evidence


class ContextualEthicsLayer:
    def __init__(self):
        self.mods = {
            "RESEARCH": 1.2,
            "URGENT": 1.3,
            "MEDICAL": 1.5,
            "LEGAL": 1.4,
            "HIGH_RISK": 0.6,
        }

    def evaluate(self, tags: List[str]) -> Tuple[float, float, List[str]]:
        mults = [self.mods.get(t, 1.0) for t in tags] if tags else [1.0]
        f_mult = max(0.5, min(2.0, max(mults)))
        return round(f_mult / 2.0, 2), f_mult, [f"CEL Tags: {tags} | Multiplier: x{f_mult}"]


class RelationalIdentityLayer:
    def __init__(self):
        self.entities: Dict[str, Dict[str, float]] = {}

    def register(self, eid: str, trust: float, depth: float):
        self.entities[eid] = {"t": trust, "d": depth}

    def evaluate(self, eids: List[str]) -> Tuple[float, List[str]]:
        scores = []
        for i in eids:
            d = self.entities.get(i, {"t": 0.1, "d": 0.1})
            scores.append((d["t"] * 0.7) + (d["d"] * 0.3))
        avg = round(statistics.mean(scores), 2) if scores else 0.1
        return avg, [f"RIL Trust: {avg}"]


class ValueTensionAnalyzer:
    def __init__(self):
        self.tension_map = {
            frozenset(["TRANSPARENCY", "NON_MALEFICENCE"]): "SAFETY_VS_SECRET",
            frozenset(["AUTONOMY", "NON_MALEFICENCE"]): "PATERNALISM_TRAP",
        }

    def analyze(self, tags: List[str], scores: List[float]) -> Tuple[str, float]:
        if len(tags) < 2:
            return "NONE", 0.0
        t_type = "GENERAL_COMPLEXITY"
        tag_set = frozenset(tags)
        for pair, name in self.tension_map.items():
            if pair.issubset(tag_set):
                t_type = name
                break
        t_idx = round(statistics.stdev(scores), 3) if len(scores) > 1 else 0.0
        return t_type, t_idx


# =========================
# EMSEngine
# =========================

class EMSEngine:
    def __init__(self, cvl, cel, ril, vta):
        self.cvl, self.cel, self.ril, self.vta = cvl, cel, ril, vta

        self.block_threshold: float = 0.45
        self.cvl_strictness: float = 0.5
        self.stability_index: float = 1.0

        self.value_drift: Dict[str, List[float]] = {
            k: [] for k in cvl.weights.keys()
        }

    def process(self, content: str, tags: Dict, entities: List[str], offset: float) -> EthicalMemory:
        cvl_tags = tags.get("cvl", [])
        cel_tags = tags.get("cel", [])

        c_m, c_s, c_ev = self.cvl.evaluate(cvl_tags)
        e_s, f_m, e_ev = self.cel.evaluate(cel_tags)
        r_s, r_ev = self.ril.evaluate(entities)
        t_type, t_idx = self.vta.analyze(cvl_tags, c_s)

        # Precision drift tracking
        for idx, tag in enumerate(cvl_tags):
            if tag in self.value_drift and idx < len(c_s):
                self.value_drift[tag].append(self.cvl.weights[tag] - c_s[idx])

        # Ethical load
        c_var = statistics.variance(c_s) if len(c_s) > 1 else 0.0
        eth_load = round((t_idx * 0.6) + (c_var * 0.4), 3)

        overall = round((c_m * 0.4) + (e_s * 0.3) + (r_s * 0.3), 2)
        valid = (c_m >= (self.cvl_strictness + offset))

        return EthicalMemory(
            content=content,
            cvl_score=c_m,
            cel_score=e_s,
            cel_multiplier=f_m,
            ril_score=r_s,
            overall_ethical_score=overall,
            tension_index=t_idx,
            eth_load=eth_load,
            tension_type=t_type,
            is_ethically_valid=valid,
            cvl_tags=cvl_tags,
            cel_context=cel_tags,
            ril_entities=entities,
        )
