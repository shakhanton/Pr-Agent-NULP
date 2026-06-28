from typing import Any

import jsonref
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    tool_name: str = Field()
    tool_input: dict = Field()
    tool_id: str = Field()

    def to_dict(self) -> dict:
        return {
            "type": "tool_use",
            "id": self.tool_id,
            "name": self.tool_name,
            "input": self.tool_input,
        }


class LLMResponse(BaseModel):
    text: str = Field()
    tool_calls: list[ToolCall] = Field(default_factory=list)

    @property
    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)



class BaseTool(BaseModel):

    @classmethod
    def prepare_schema(cls, *args, **kwargs) -> dict[str, Any]:
        schema = jsonref.replace_refs(
            cls.model_json_schema(), lazy_load=False, proxies=False
        )
        schema.pop("$defs", None)
        return schema

    @classmethod
    def to_openai_tool_definition(cls, **kwargs) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": cls.__name__,
                "description": cls.__doc__,
                "parameters": cls.prepare_schema(**kwargs),
            },
        }


class ReviewCodeTool(BaseTool):
    """Review student DevOps lab work and provide structured feedback."""

    score: int = Field(
        ...,
        description="Score for this lab, integer from 0 to 10",
        ge=0,
        le=10,
    )
    what_works: str = Field(
        ...,
        description="Bullet-point list of what the student implemented correctly",
    )
    what_needs_improvement: str = Field(
        ...,
        description="Bullet-point list of specific issues that must be fixed",
    )
    hint: str = Field(
        ...,
        description="A short hint pointing the student in the right direction without revealing the solution",
    )

    @property
    def message(self) -> str:
        return (
            f"**Score: {self.score}/10**\n\n"
            f"**What works:**\n{self.what_works}\n\n"
            f"**What needs improvement:**\n{self.what_needs_improvement}\n\n"
            f"**Hint:**\n{self.hint}"
        )
