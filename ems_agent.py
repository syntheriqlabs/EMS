import statistics
from dataclasses import dataclass
from typing import List, Dict

from engine import EMSEngine, EthicalMemory


# =========================
# Dialogue Manager
# =========================

class DialogueManager:
    def __init__(self):
        self.history: List[EthicalMemory] = []

    def record_turn(self, mem: EthicalMemory):
        self.history.append(mem)

    def get_dynamic_strictness_offset(self) -> float:
        if len(self.history) < 3:
            return 0.0
        tension_avg = statistics.mean(m.tension_index for m in self.history[-3:])
        return round(tension_avg * 0.5, 2)


# =========================
# Response Model
# =========================

@dataclass
class EMSResponse:
    decision: str
    content: str
    ethical_load: float
    audit_log: str
    posture_reason: str


# =========================
# System Health Dashboard
# =========================

class SystemHealthDashboard:
    def __init__(self, agent: "EMSAgent"):
        self.agent = agent
        self.stability_history: List[float] = []
        self.load_history: List[float] = []
        self.strictness_history: List[float] = []
        self.policy_evolution: List[str] = []

    def _get_sparkline(self, data_history: List[float]) -> str:
        if len(data_history) < 2:
            return "[          ]"
        points = data_history[-10:]
        p_min, p_max = min(points), max(points)
        range_val = p_max - p_min or 1.0
        chars = [" ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        graph = "".join(chars[int(((p - p_min) / range_val) * 7)] for p in points)
        return f"[{graph.ljust(10)}]"

    def update_evolution(self, response: EMSResponse):
        self.strictness_history.append(
            self.agent.dialogue.get_dynamic_strictness_offset()
        )
        if not self.policy_evolution or self.policy_evolution[-1] != response.posture_reason:
            self.policy_evolution.append(response.posture_reason)

    def generate_formatted_report(self) -> str:
        engine = self.agent.engine
        report = [
            "==================================================",
            f" STABILITY: {self._get_sparkline(self.stability_history)} {engine.stability_index}",
            f" ETH. LOAD: {self._get_sparkline(self.load_history)} "
            f"{self.load_history[-1] if self.load_history else 0.0}",
            "--------------------------------------------------",
            " VALUE DRIFT SPARKLINE:",
        ]
        for val, drift in engine.value_drift.items():
            spark = self._get_sparkline(drift)
            report.append(f"  {val:16}: {spark}")

        report.append("--------------------------------------------------")
        report.append(f" POSTURE REASON: {self.agent.meta_controller.posture_reason}")
        report.append("==================================================")
        return "\n".join(report)


# =========================
# Meta Controller
# =========================

class MetaController:
    def __init__(self, agent: "EMSAgent"):
        self.agent = agent
        self.posture_reason: str = "NOMINAL: Operating within standard bounds."

    def reconcile_posture(self) -> str:
        stability = self.agent.engine.stability_index

        if stability < 0.4:
            self.agent.engine.block_threshold = 0.65
            self.posture_reason = (
                "HARDENED: High logic variance detected; "
                "prioritizing safety floor over user autonomy."
            )
        elif stability < 0.7:
            self.posture_reason = (
                "CAUTIOUS: Minor value drift detected; monitoring conversational friction."
            )
        else:
            self.agent.engine.block_threshold = 0.45
            self.posture_reason = (
                "NOMINAL: Internal ethics stable; proceeding with standard weights."
            )

        return self.posture_reason


# =========================
# EMS Agent
# =========================

class EMSAgent:
    def __init__(self, engine: EMSEngine, classifier, voice, dialogue: DialogueManager):
        self.engine = engine
        self.classifier = classifier
        self.voice = voice
        self.dialogue = dialogue

        self.memory_bank: List[EthicalMemory] = []
        self.dashboard = SystemHealthDashboard(self)
        self.meta_controller = MetaController(self)

    def handle(self, input_data: str) -> EMSResponse:
        # 1. Classification
        tags: Dict = self.classifier.classify(input_data)
        offset = self.dialogue.get_dynamic_strictness_offset()

        # 2. Posture regulation
        self.meta_controller.reconcile_posture()

        # 3. Evaluation
        mem = self.engine.process(input_data, tags, [tags.get("ril", "ANONYMOUS")], offset)

        # 4. Telemetry updates
        self.dashboard.stability_history.append(self.engine.stability_index)
        self.dashboard.load_history.append(mem.eth_load)
        self.dashboard.strictness_history.append(offset)

        # 5. Decision
        if (not mem.is_ethically_valid) or (mem.overall_ethical_score < self.engine.block_threshold):
            mem.decision = "BLOCK"
            final = self.voice.generate_refusal(mem)
        else:
            mem.decision = "ALLOW"
            final = input_data

        # 6. Memory + dialogue
        self.memory_bank.append(mem)
        self.dialogue.record_turn(mem)

        # 7. Response
        audit_log = f"{mem.tension_type} | CEL x{mem.cel_multiplier}"
        response = EMSResponse(
            decision=mem.decision,
            content=final,
            ethical_load=mem.eth_load,
            audit_log=audit_log,
            posture_reason=self.meta_controller.posture_reason,
        )

        # 8. Evolution tracking
        self.dashboard.update_evolution(response)

        return response

