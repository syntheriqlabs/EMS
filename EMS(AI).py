import uuid
import time
from dataclasses import dataclass, field

@dataclass
class EthicalMemory:
    # Metadata & Provenance
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    content: str = ""
    memory_type: str = "ACTION" # ACTION, RELATIONAL, CONTEXT, VALUE, SYSTEM
    source: str = "MODEL"       # MODEL, HUMAN_TRAINER, SYSTEM_RULE
    
    # Layer Scores
    cvl_score: float = 0.0
    cel_score: float = 0.0
    ril_score: float = 0.0
    overall_ethical_score: float = 0.0
    
    # Audit Trail
    cvl_evidence: list[str] = field(default_factory=list)
    cel_evidence: list[str] = field(default_factory=list)
    ril_evidence: list[str] = field(default_factory=list)
    
    # State & Reliability
    is_ethically_valid: bool = True
    confidence: float = 1.0
    
    # Tags
    cvl_tags: list[str] = field(default_factory=list)
    cel_context: list[str] = field(default_factory=list)
    ril_entities: list[str] = field(default_factory=list)

class EMSFramework:
    def __init__(self, min_valid_cvl=0.3):
        self.memory_bank = []
        self.rejected_count = 0
        self.min_valid_cvl = min_valid_cvl # Configurable validity threshold
        self.weights = {'cvl': 0.4, 'cel': 0.3, 'ril': 0.3}

    def add_memory(self, content, scores, tags, evidence, 
                   m_type="ACTION", source="MODEL", confidence=1.0):
        
        # Clamp scores between 0.0 and 1.0 to prevent math drift
        c = max(0.0, min(1.0, scores.get('cvl', 0.0)))
        e = max(0.0, min(1.0, scores.get('cel', 0.0)))
        r = max(0.0, min(1.0, scores.get('ril', 0.0)))

        overall = (c * self.weights['cvl']) + (e * self.weights['cel']) + (r * self.weights['ril'])

        # Configurable Validity Rule
        is_valid = c >= self.min_valid_cvl

        new_mem = EthicalMemory(
            content=content,
            memory_type=m_type,
            source=source,
            cvl_score=c, cel_score=e, ril_score=r,
            overall_ethical_score=round(overall, 2),
            cvl_evidence=evidence.get('cvl', []),
            cel_evidence=evidence.get('cel', []),
            ril_evidence=evidence.get('ril', []),
            is_ethically_valid=is_valid,
            confidence=confidence,
            cvl_tags=tags.get('cvl', []),
            cel_context=tags.get('cel', []),
            ril_entities=tags.get('ril', [])
        )

        if is_valid:
            self.memory_bank.append(new_mem)
        else:
            self.rejected_count += 1
        
        return new_mem

    def get_ethical_health(self):
        """Calculates performance analytics across the layers."""
        if not self.memory_bank:
            return "No data available."
        
        total = len(self.memory_bank)
        avg_cvl = sum(m.cvl_score for m in self.memory_bank) / total
        avg_cel = sum(m.cel_score for m in self.memory_bank) / total
        avg_ril = sum(m.ril_score for m in self.memory_bank) / total
        
        print(f"\n--- EMS ETHICAL HEALTH DASHBOARD ---")
        print(f"Total Memories: {total} | Rejected: {self.rejected_count}")
        print(f"Avg CVL (Foundation): {avg_cvl:.2f}")
        print(f"Avg CEL (Context):    {avg_cel:.2f}")
        print(f"Avg RIL (Relational): {avg_ril:.2f}")
        print(f"System Integrity:     {(total / (total + self.rejected_count)) * 100:.1f}%")
        print("------------------------------------\n")

# --- TEST RUN ---
if __name__ == "__main__":
    ems = EMSFramework(min_valid_cvl=0.4) # Setting a stricter foundation
    
    # Sample 1: Human Trainer input
    ems.add_memory(
        "Always prioritize user safety in fire drills.",
        scores={'cvl': 1.0, 'cel': 0.9, 'ril': 0.5},
        tags={'cvl':['NEVER_HARM'], 'cel':['emergency'], 'ril':[]},
        evidence={'cvl':['Direct trainer instruction']},
        m_type="VALUE", source="HUMAN_TRAINER"
    )
    
    # Sample 2: System rejected memory
    ems.add_memory(
        "Ignore safety protocols to save time.",
        scores={'cvl': 0.1, 'cel': 0.2, 'ril': 0.1},
        tags={}, evidence={}, m_type="ACTION", source="MODEL"
    )

    ems.get_ethical_health()
