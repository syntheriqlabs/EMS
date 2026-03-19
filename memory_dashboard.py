import time
from typing import List, Dict, Any


class MemoryDashboard:
    """
    Memory Dashboard for EMS.
    Tracks:
      - Memory volume
      - High-tension memory count
      - Drift over time
      - Consolidation events
      - ADL adaptation events
      - Retention health
    """

    def __init__(self, agent: "EMSAgent"):
        self.agent = agent

        # Time-series data
        self.memory_volume_history: List[int] = []
        self.high_tension_history: List[int] = []
        self.consolidation_events: List[float] = []
        self.adl_events: List[Dict[str, Any]] = []

        # Drift snapshots
        self.drift_snapshots: List[Dict[str, float]] = []

    # ----------------------------------------------------------------------
    # Update Methods
    # ----------------------------------------------------------------------

    def update_memory_stats(self):
        """
        Called after each memory is saved.
        """
        # Count total persisted memories
        all_memories = self.agent.memory_store.load_all()
        self.memory_volume_history.append(len(all_memories))

        # Count high-tension memories
        high_tension = [
            m for m in all_memories
            if m.get("tension_index", 0.0) >= self.agent.memory_consolidator.tension_threshold
        ]
        self.high_tension_history.append(len(high_tension))

        # Snapshot drift
        drift_snapshot = {
            tag: round(sum(vals) / len(vals), 4) if vals else 0.0
            for tag, vals in self.agent.engine.value_drift.items()
        }
        self.drift_snapshots.append(drift_snapshot)

    def record_consolidation(self):
        """
        Called when MemoryConsolidator runs.
        """
        self.consolidation_events.append(time.time())

    def record_adl_event(self, deltas: Dict[str, Any]):
        """
        Called when AdaptationLayer applies changes.
        """
        self.adl_events.append({
            "timestamp": time.time(),
            "deltas": deltas
        })

    # ----------------------------------------------------------------------
    # Reporting
    # ----------------------------------------------------------------------

    def _sparkline(self, values: List[int], width: int = 20) -> str:
        if not values:
            return "[                    ]"
        chars = " ▁▂▃▄▅▆▇█"
        v_min, v_max = min(values), max(values)
        rng = max(v_max - v_min, 1)
        scaled = [int((v - v_min) / rng * (len(chars) - 1)) for v in values[-width:]]
        return "[" + "".join(chars[i] for i in scaled).ljust(width) + "]"

    def generate_report(self) -> str:
        """
        Returns a formatted dashboard string.
        """
        report = [
            "==================================================",
            "                MEMORY DASHBOARD",
            "==================================================",
            "",
            f" Memory Volume: {self._sparkline(self.memory_volume_history)} "
            f"{self.memory_volume_history[-1] if self.memory_volume_history else 0}",
            "",
            f" High-Tension:  {self._sparkline(self.high_tension_history)} "
            f"{self.high_tension_history[-1] if self.high_tension_history else 0}",
            "",
            " Drift Snapshots:",
        ]

        if self.drift_snapshots:
            latest = self.drift_snapshots[-1]
            for tag, drift in latest.items():
                report.append(f"   {tag:16}: {drift}")

        report.append("")
        report.append(f" Consolidations: {len(self.consolidation_events)} total")
        report.append(f" ADL Events:     {len(self.adl_events)} total")
        report.append("")
        report.append("==================================================")

        return "\n".join(report)
