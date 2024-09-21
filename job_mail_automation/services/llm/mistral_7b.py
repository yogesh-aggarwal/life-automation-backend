from huggingface_hub import InferenceClient

from job_mail_automation.core.constants import HF_API_KEY
from job_mail_automation.types.llm import LLMService


class Mistral7B(LLMService):
    model = "mistralai/Mistral-7B-Instruct-v0.3"

    def run(self, messages):
        client = InferenceClient(model=self.model, token=HF_API_KEY)

        res = client.chat_completion(
            messages.to_dict(),
            temperature=0,
            max_tokens=10_000,
        )
        if not res.choices:
            return None
        res = res.choices[0].message

        return res.content
