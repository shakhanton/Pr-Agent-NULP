from json import loads, JSONDecodeError

from loguru import logger
from openai import OpenAI

from configs.gemini import GeminiConfig
from models.llm.tools import BaseTool, LLMResponse, ToolCall


class GeminiClient:
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

    def __init__(self):
        self.__config = GeminiConfig()  # type: ignore
        self.__client = OpenAI(
            api_key=self.__config.API_KEY,
            base_url=self.BASE_URL,
        )

    def send_message(self, messages: list, tools: list[type[BaseTool]] | None = None) -> LLMResponse:
        prepared_tools = [tool.to_openai_tool_definition() for tool in tools] if tools else None
        kwargs = {"model": self.__config.MODEL, "messages": messages}
        if prepared_tools:
            kwargs["tools"] = prepared_tools
            kwargs["tool_choice"] = "required"

        response = self.__client.chat.completions.create(**kwargs)
        return self.__parse_response(response)

    @staticmethod
    def __parse_response(response) -> LLMResponse:
        if not response.choices:
            raise ValueError("No choices in Gemini API response")

        choice = response.choices[0]

        if not choice.message.tool_calls:
            raise ValueError("No tool calls in Gemini API response")

        tool_calls = []
        for call in choice.message.tool_calls:
            try:
                arguments = (
                    loads(call.function.arguments)
                    if isinstance(call.function.arguments, str)
                    else call.function.arguments
                )
            except JSONDecodeError as e:
                logger.warning(f"Error decoding tool call arguments: {e}")
                raise RuntimeError("Couldn't decode tool call arguments") from e

            tool_calls.append(ToolCall(
                tool_name=call.function.name,
                tool_input=arguments,
                tool_id=call.id,
            ))

        return LLMResponse(
            text=choice.message.content or "",
            tool_calls=tool_calls,
        )
