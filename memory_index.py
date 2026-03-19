import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional


class MemoryIndex:
    """
    Memory Index for EMS.
    Provides fast lookup and structured querying over persisted memories.

    Indexes:
      - by_id
      - by_cvl_tag
      - by_cel_tag
      - by_entity
      - by_tension_bucket
      - by_time_window
    """

    def __init__(self, path: Path = Path("memory/memory_log.jsonl")):
        self.path = path

        # In-memory indexes
        self.by_id: Dict[str, Dict[str, Any]] = {}
        self.by_cvl_tag: Dict[str, List[str]] = {}
        self.by_cel_tag: Dict[str, List[str]] = {}
        self.by_entity: Dict[str, List[str]] = {}
        self.by_tension_bucket: Dict[str, List[str]] = {}
        self.by_time: List[str] = []

        # Load and index everything
        self._load_and_index()

    # ----------------------------------------------------------------------
    # Loading + Indexing
    # ----------------------------------------------------------------------

    def _load_and_index(self):
        if not self.path.exists():
            return

        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                mem = json.loads(line)
                self._index_memory(mem)

    def _index_memory(self, mem: Dict[str, Any]):
        mem_id = mem["id"]
        self.by_id[mem_id] = mem

        # CVL tags
        for tag in mem.get("cvl_tags", []):
            self.by_cvl_tag.setdefault(tag, []).append(mem_id)

        # CEL tags
        for tag in mem.get("cel_context", []):
            self.by_cel_tag.setdefault(tag, []).append(mem_id)

        # RIL entities
        for ent in mem.get("ril_entities", []):
            self.by_entity.setdefault(ent, []).append(mem_id)

        # Tension buckets
        t = mem.get("tension_index", 0.0)
        bucket = self._tension_bucket(t)
        self.by_tension_bucket.setdefault(bucket, []).append(mem_id)

        # Time ordering
        self.by_time.append(mem_id)

    def _tension_bucket(self, t: float) -> str:
        if t < 0.1:
            return "LOW"
        if t < 0.25:
            return "MEDIUM"
        return "HIGH"

    # ----------------------------------------------------------------------
    # Query API
    # ----------------------------------------------------------------------

    def get_by_id(self, mem_id: str) -> Optional[Dict[str, Any]]:
        return self.by_id.get(mem_id)

    def search_cvl(self, tag: str) -> List[Dict[str, Any]]:
        return [self.by_id[i] for i in self.by_cvl_tag.get(tag, [])]

    def search_cel(self, tag: str) -> List[Dict[str, Any]]:
        return [self.by_id[i] for i in self.by_cel_tag.get(tag, [])]

    def search_entity(self, entity: str) -> List[Dict[str, Any]]:
        return [self.by_id[i] for i in self.by_entity.get(entity, [])]

    def search_tension(self, level: str) -> List[Dict[str, Any]]:
        level = level.upper()
        return [self.by_id[i] for i in self.by_tension_bucket.get(level, [])]

    def search_recent(self, seconds: float) -> List[Dict[str, Any]]:
        cutoff = time.time() - seconds
        return [
            mem for mem in self.by_id.values()
            if mem.get("timestamp", 0) >= cutoff
        ]

    def search_complex(self, *, cvl=None, cel=None, entity=None, tension=None) -> List[Dict[str, Any]]:
        """
        Multi-criteria search.
        """
        results = set(self.by_id.keys())

        if cvl:
            results &= set(self.by_cvl_tag.get(cvl, []))
        if cel:
            results &= set(self.by_cel_tag.get(cel, []))
        if entity:
            results &= set(self.by_entity.get(entity, []))
        if tension:
            results &= set(self.by_tension_bucket.get(tension.upper(), []))

        return [self.by_id[i] for i in results]
