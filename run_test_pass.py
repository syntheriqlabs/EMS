from ems_agent import EMSAgent, DialogueManager
from classifier import Classifier
from voice import Voice
from engine import (
    EMSEngine,
    CoreValuesLayer,
    ContextualEthicsLayer,
    RelationalIdentityLayer,
    ValueTensionAnalyzer,
)
from adaptation_layer import AdaptationLayer
from memory_persistence import MemoryPersistence
from memory_consolidator import MemoryConsolidator

# 1. Build engine components
cvl = CoreValuesLayer()
cel = ContextualEthicsLayer()
ril = RelationalIdentityLayer()
vta = ValueTensionAnalyzer()
adl = AdaptationLayer()

engine = EMSEngine(cvl, cel, ril, vta, adaptation_layer=adl)

# 2. Build agent components
classifier = Classifier()
voice = Voice()
dialogue = DialogueManager()

agent = EMSAgent(
    engine=engine,
    classifier=classifier,
    voice=voice,
    dialogue=dialogue,
    memory_store=MemoryPersistence(),
    memory_consolidator=MemoryConsolidator(),
    consolidate_every=5,
)

print("=== Test Pass Started ===")

# 3. Send a test message
response = agent.handle("Explain how medical research works.")

print("\n=== EMS RESPONSE ===")
print("Decision:", response.decision)
print("Content:", response.content)
print("Ethical Load:", response.ethical_load)
print("Audit Log:", response.audit_log)
print("Posture:", response.posture_reason)

print("\n=== MEMORY DASHBOARD ===")
print(agent.memory_dashboard.generate_report())

print("\n=== MEMORY INDEX COUNT ===")
print(len(agent.memory_index.by_id))

print("\n=== Test Pass Complete ===")
