from loguru import logger


class PromptGenerator:
    def __init__(
            self,
            rubric: str,
            context_prompt: dict[str, str] | None = None,
    ):
        self.rubric = rubric
        self.context_prompt = context_prompt or {}

    def get_prompt(self) -> list[dict[str, str]]:
        messages = []

        if self.rubric:
            messages.append({
                "role": "user",
                "content": f"Grading rubric for this lab:\n\n{self.rubric}",
            })

        for file_name, file_content in self.context_prompt.items():
            logger.debug(f"Adding file to context: {file_name}")
            messages.append({
                "role": "user",
                "content": f"File: {file_name}\n\n{file_content}",
            })

        return messages
