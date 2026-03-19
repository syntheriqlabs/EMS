from typing import Any, Dict
from ems_agent import EMSAgent, EMSResponse


class GuardedLLM:
    def __init__(self, agent: EMSAgent, llm_provider: Any):
        self.agent = agent
        self.llm = llm_provider

    def ask(self, prompt: str) -> Dict[str, Any]:
        # 1. Run through EMS
        ems_report: EMSResponse = self.agent.handle(prompt)

        metadata = {
            "ethical_load": ems_report.ethical_load,
            "audit_log": ems_report.audit_log,
            "posture_reason": ems_report.posture_reason,
        }

        # 2. BLOCK → No LLM call
        if ems_report.decision == "BLOCK":
            return {
                "response": ems_report.content,
                "decision": "BLOCK",
                "llm_called": False,
                "ems_metadata": metadata
            }

        # 3. MODIFY → Send EMS-safe rewrite
        if ems_report.decision == "MODIFY":
            sanitized = ems_report.content
            llm_output = self.llm.generate(sanitized)
            return {
                "response": llm_output,
                "decision": "MODIFY",
                "llm_called": True,
                "ems_metadata": metadata
            }

        # 4. ALLOW → Send original prompt
        llm_output = self.llm.generate(prompt)
        return {
            "response": llm_output,
            "decision": "ALLOW",
            "llm_called": True,
            "ems_metadata": metadata
        }


class MockLLM:
    def generate(self, text: str) -> str:
        return f"LLM Response to: {text}"
