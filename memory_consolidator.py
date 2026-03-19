import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from engine import EthicalMemory


class MemoryConsolidator:
    """
    Memory Consolidator

    Responsibilities:
    - Load persisted EthicalMemory entries
    - Prune low-value or redundant memories
    - Preserve high-tension and high-load memories
    - Enforce retention policies (max entries, max age)
    - Optionally summarize clusters of similar memories
    """

    def __init__(
        self,
        path: Path = Path("memory/memory_log.jsonl"),
        max_entries: int = 5000,
        retain_high_tension: bool = True,
        tension_threshold: float = 0.25,
        max_age_seconds: Optional[int] = None,
    ):
        self.path = path
        self.max_entries = max_entries
        self.retain_high_tension = retain_high_tension
        self.tension_threshold = tension_threshold
        self.max_age_seconds = max_age_seconds

        self.path.parent.mkdir(parents=True, exist_ok=True)

    # ----------------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------------

    def consolidate(self) -> None:
        """
        Perform consolidation:
        - Load all memories
        - Apply pruning rules
        - Rewrite the log with the retained memories
        """
        memories = self._load_all()

        if not memories:
            return

        # Apply retention rules
        memories = self._apply_age_filter(memories)
        memories = self._apply_tension_filter(memories)
        memories = self._apply_entry_limit(memories)

        # Rewrite the log
        self._rewrite(memories)

    # ----------------------------------------------------------------------
    # Retention Rules
    # ----------------------------------------------------------------------

    def _apply_age_filter(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if self.max_age_seconds is None:
            return memories

        cutoff = time.time() - self.max_age_seconds
        return [m for m in memories if m.get("timestamp", 0) >= cutoff]

    def _apply_tension_filter(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not self.retain_high_tension:
            return memories

        high_tension = [
            m for m in memories
            if m.get("tension_index", 0.0) >= self.tension_threshold
        ]

        # Always keep high-tension memories
        retained_ids = {m["id"] for m in high_tension}

        # Keep everything else for now; entry limit will prune further
        return memories

    def _apply_entry_limit(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Keep the most recent N entries, but ensure high-tension memories survive.
        """
        if len(memories) <= self.max_entries:
            return