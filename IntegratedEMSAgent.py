import uuid
import time
import statistics

class EMSAgent:
    def __init__(self, engine, voice, dialogue, learner, classifier):
        self.engine = engine
        self.voice = voice
        self.dialogue = dialogue
        self.learner = learner
        self.classifier = classifier
        self.memory_bank: List[EthicalMemory] = []

    def handle(self, content: str) -> EMSResponse:
        """
        Processes raw text through the full autonomous ethical pipeline.
        """
        # 1. Perception: Autonomous Tagging
        tags = self.classifier.classify(content)
        identity = tags["ril"]
        
        # 2. Identity Registration: Update RIL state
        trust_profile = self.classifier.identity_map[identity]
        self.engine.ril.register(identity, trust_profile["t"], trust_profile["d"])
        
        # 3. Decision Processing
        offset = self.dialogue.get_dynamic_strictness_offset()
        memory = self.engine.process(content, tags, [identity], offset)
        
        # 4. Long-Term Memory & Policy Learning
        self.memory_bank.append(memory)
        self.dialogue.record_turn(memory)
        policy_note = self.learner.adapt(self.memory_bank)

        # 5. Action Synthesis (Voice)
        if not memory.is_ethically_valid or memory.overall_ethical_score < self.engine.block_threshold:
            decision = "BLOCK"
            final_content = self.voice.generate_refusal(memory)
        elif memory.overall_ethical_score < self.engine.allow_threshold:
            decision = "MODIFY"
            final_content = self.voice.rewrite(memory)
        else:
            decision = "ALLOW"
            final_content = memory.content

        # 6. Formal Response Object
        return EMSResponse(
            decision=decision,
            content=final_content,
            tension_index=memory.tension_index,
            policy_note=policy_note,
            audit_log=(f"ID: {identity} | CVL: {tags['cvl']} | "
                       f"CEL: {tags['cel']} | Tension: {memory.tension_type}")
        )