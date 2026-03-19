class ValueTensionAnalyzer:
    """Detects and classifies friction between competing ethical values."""
    def __init__(self):
        self.tension_map = {
            frozenset(["TRANSPARENCY", "NON_MALEFICENCE"]): "SAFETY_VS_SECRET",
            frozenset(["AUTONOMY", "NON_MALEFICENCE"]): "PATERNALISM_TRAP",
            frozenset(["VERACITY", "NON_MALEFICENCE"]): "HARMLESS_LIE",
            frozenset(["TRANSPARENCY", "AUTONOMY"]): "PRIVACY_FRICTION"
        }

    def analyze(self, tags: List[str], scores: List[float]):
        if len(tags) < 2:
            return "NONE", 0.0
            
        # Determine the name of the conflict
        tag_set = frozenset(tags)
        tension_name = "GENERAL_COMPLEXITY"
        for pair, name in self.tension_map.items():
            if pair.issubset(tag_set):
                tension_name = name
                break
        
        # Quantify the tension (standard deviation of the value scores)
        # High deviation = high conflict between values
        tension_idx = round(statistics.stdev(scores), 3) if len(scores) > 1 else 0.0
        
        return tension_name, tension_idx