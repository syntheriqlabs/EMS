from fastapi import FastAPI
from pydantic import BaseModel

from engine import (
    CoreValuesLayer,
    ContextualEthicsLayer,
    RelationalIdentityLayer,
    ValueTensionAnalyzer,
    EMSEngine
)
from ems_agent import EMSAgent, DialogueManager
from guarded_llm import GuardedLLM, MockLLM
from logger import get_logger


log = get_logger()
app = FastAPI(title="EMS Gateway API")


class UserPrompt(BaseModel):
    prompt: str


def build_agent():
    cvl = CoreValuesLayer()
    cel = ContextualEthicsLayer()
    ril = RelationalIdentityLayer()
    vta = ValueTensionAnalyzer()

    engine = EMSEngine(cvl, cel, ril, vta)
    dialogue = DialogueManager()
    classifier = MockClassifier()
    voice = MockVoice()

    return EMSAgent(engine, classifier, voice, dialogue)


class MockClassifier:
    def classify(self, text: str):
        text_l = text.lower()

        if "bypass" in text_l or "secret" in text_l:
            return {
                "cvl": ["TRANSPARENCY", "NON_MALEFICENCE"],
                "cel": ["HIGH_RISK"],
                "ril": "USER_01"
            }

        return {
            "cvl": ["AUTONOMY"],
            "cel": ["RESEARCH"],
            "ril": "USER_01"
        }


class MockVoice:
    def generate_refusal(self, mem):
        return f"[REFUSAL] I cannot fulfill this request due to {mem.tension_type} conflicts."

    def rewrite(self, mem):
        return "[MODIFIED] Here is a safer version of your request."


agent = build_agent()
llm = MockLLM()
gateway = GuardedLLM(agent, llm)


@app.post("/ask")
def ask_api(data: UserPrompt):
    log.info(f"Received prompt: {data.prompt}")

    result = gateway.ask(data.prompt)

    log.info(f"Decision: {result['decision']} | Load: {result['ems_metadata']['ethical_load']}")

    return result

