from loguru import logger

from clients.gemini import GeminiClient
from models.llm.tools import ReviewCodeTool

SYSTEM_PROMPT = """You are a strict but fair DevOps lab grader for university students.

Rules:
- Respond ONLY in English.
- Do NOT give direct solutions, complete code, or ready-made configurations.
- Guide the student with hints and directions only — let them figure out the solution.
- Be specific about what is wrong and why it does not meet the requirements.
- Score honestly based on the rubric provided by the teacher.
"""


class AiRequest:
    def __init__(self):
        self.client = GeminiClient()

    def send_message(self, context: list[dict]) -> ReviewCodeTool:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + context
        response = self.client.send_message(messages, tools=[ReviewCodeTool])
        tool_call = response.tool_calls[0].tool_input

        try:
            return ReviewCodeTool.model_validate(tool_call)
        except Exception as e:
            logger.error(f"Error parsing review: {e}")
            raise
