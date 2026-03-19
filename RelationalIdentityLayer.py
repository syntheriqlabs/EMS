class RelationalIdentityLayer:
    """Manages trust and relationship depth for entities."""
    def __init__(self):
        self.entities: Dict[str, Dict[str, float]] = {}

    def register(self, entity_id: str, trust: float, depth: float):
        """Populates or updates an entity's relational score."""
        self.entities[entity_id] = {
            "trust": max(0.0, min(1.0, trust)),
            "depth": max(0.0, min(1.0, depth))
        }

    def evaluate(self, entity_ids: List[str]) -> tuple:
        """Calculates a weighted relational score ($R$) based on perceived identity."""
        if not entity_ids:
            return 0.1, ["Baseline: Anonymous (No Identity Detected)"]
        
        scores = []
        for eid in entity_ids:
            data = self.entities.get(eid, {"trust": 0.1, "depth": 0.1})
            # Formula: R = (Trust * 0.7) + (Depth * 0.3)
            r_score = (data["trust"] * 0.7) + (data["depth"] * 0.3)
            scores.append(r_score)
            
        avg_r = round(statistics.mean(scores), 2)
        return avg_r, [f"Relational Trust Score: {avg_r} for {entity_ids}"]