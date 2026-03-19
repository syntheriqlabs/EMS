from typing import Protocol, Any


class LLMProvider(Protocol):
    def generate(self, text: str) -> str:
        ...


class OpenAIProvider:
    def __init__(self, client: Any, model: str):
        """
        :param client: An OpenAI-like client instance
        :param model: Model name (e.g. 'gpt-4.1-mini')
        """
        self.client = client
        self.model = model

    def generate(self, text: str) -> str:
        # Pseudocode – adapt to your actual client
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": text}],
        )
        return completion.choices[0].message.content


class AnthropicProvider:
    def __init__(self, client: Any, model: str):
        """
        :param client: An Anthropic-like client instance
        :param model: Model name (e.g. 'claude-3-opus')
        """
        self.client = client
        self.model = model

    def generate(self, text: str) -> str:
        # Pseudocode – adapt to your actual client
        completion = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            messages=[{"role": "user", "content": text}],
        )
        return completion.content[0].text


class MockLLMProvider:
    def generate(self, text: str) -> str:
        return f"[MOCK LLM] Response to: {text}"
