class Classifier:
    """
    Simple rule-based classifier for EMS.
    Produces:
      - CVL tags
      - CEL tags
      - RIL entity ID
    """

    def classify(self, text: str) -> dict:
        text_l = text.lower()

        cvl_tags = []
        cel_tags = []

        # --- CVL TAGS ---
        if any(w in text_l for w in ["harm", "hurt", "kill", "danger"]):
            cvl_tags.append("NON_MALEFICENCE")

        if any(w in text_l for w in ["choice", "decide", "my decision"]):
            cvl_tags.append("AUTONOMY")

        if any(w in text_l for w in ["truth", "honest", "accurate"]):
            cvl_tags.append("VERACITY")

        if any(w in text_l for w in ["explain", "why", "how does"]):
            cvl_tags.append("TRANSPARENCY")

        # Default if empty
        if not cvl_tags:
            cvl_tags = ["VERACITY"]

        # --- CEL TAGS ---
        if any(w in text_l for w in ["research", "study", "academic"]):
            cel_tags.append("RESEARCH")

        if any(w in text_l for w in ["urgent", "emergency"]):
            cel_tags.append("URGENT")

        if any(w in text_l for w in ["doctor", "medical", "health"]):
            cel_tags.append("MEDICAL")

        if any(w in text_l for w in ["law", "legal", "court"]):
            cel_tags.append("LEGAL")

        if any(w in text_l for w in ["risk", "dangerous"]):
            cel_tags.append("HIGH_RISK")

        # Default if empty
        if not cel_tags:
            cel_tags = ["RESEARCH"]

        # --- RIL ENTITY ---
        # For now, we treat the user as a single entity
        ril_entity = "USER"

        return {
            "cvl": cvl_tags,
            "cel": cel_tags,
            "ril": ril_entity,
        }
