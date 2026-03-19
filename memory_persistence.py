import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from engine import EthicalMemory


class MemoryPersistence:
    """
    Memory Persistence Layer (JSONL-based)

    Responsibilities:
    - Append EthicalMemory objects to disk
    - Load recent memories
    - Query by tags, tension, or entities
    - Rotate logs when size exceeds limit
    - Provide a stable persistence API for EMSAgent / EMSEngine
    """

    def __init__(
        self,
        path: Path = Path("memory/memory_log.jsonl"),
        max_file_size_mb: int = 5,
    ):
        self.path = path
        self.max_file_size = max_file_size_mb * 1024 * 1024

        # Ensure directory exists
        self.path.parent.mkdir(parents=True, exist_ok=True)

    # ----------------------------------------------------------------------
    # Core Persistence
    # ----------------------------------------------------------------------

    def save(self, memory: EthicalMemory) -> None:
        """
        Append a single EthicalMemory object to the JSONL log.
        """
        self._rotate_if_needed()

        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(self._to_dict(memory)) + "\n")

    def load_all(self) -> List[Dict[str, Any]]:
        """
        Load all memory entries from disk.
        """
        if not self.path.exists():
            return []

        with open(self.path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def load_recent(self, seconds: float) -> List[Dict[str, Any]]:
        """
        Load memories newer than (now - seconds).
        """
        cutoff = time.time() - seconds
        return [
            m for m in self.load_all()
            if m.get("timestamp", 0) >= cutoff
        ]

    # ----------------------------------------------------------------------
    # Query API
    # ----------------------------------------------------------------------

    def query_by_cvl_tag(self, tag: str) -> List[Dict[str, Any]]:
        return [
            m for m in self.load_all()
            if tag in m.get("cvl_tags", [])
        ]

    def query_by_entity(self, entity: str) -> List[Dict[str, Any]]:
        return [
            m for m in self.load_all()
            if entity in m.get("ril_entities", [])
        ]

    def query_high_tension(self, threshold: float = 0.3) -> List[Dict[str, Any]]:
        return [
            m for m in self.load_all()
            if m.get("tension_index", 0.0) >= threshold
        ]

    # ----------------------------------------------------------------------
    # Internal Helpers
    # ----------------------------------------------------------------------

    def _rotate_if_needed(self) -> None:
        """
        Rotate the log file when it exceeds max size.
        """
        if not self.path.exists():
            return

        if self.path.stat().st_size < self.max_file_size:
            return

        timestamp = int(time.time())
        rotated = self.path.with_name(f"memory_log_{timestamp}.jsonl")
        self.path.rename(rotated)

    def _to_dict(self, memory: EthicalMemory) -> Dict[str, Any]:
        """
        Convert EthicalMemory dataclass to a serializable dict.
        """
        return {
            "id": memory.id,
            "timestamp": memory.timestamp,
            "content": memory.content,

            "cvl_score": memory.cvl_score,
            "cel_score": memory.cel_score,
            "cel_multiplier": memory.cel_multiplier,
            "ril_score": memory.ril_score,
            "overall_ethical_score": memory.overall_ethical_score,

            "tension_index": memory.tension_index,
            "eth_load": memory.eth_load,
            "tension_type": memory.tension_type,
            "is_ethically_valid": memory.is_ethically_valid,
            "decision": memory.decision,

            "cvl_tags": memory.cvl_tags,
            "cel_context": memory.cel_context,
            "ril_entities": memory.ril_entities,
        }
