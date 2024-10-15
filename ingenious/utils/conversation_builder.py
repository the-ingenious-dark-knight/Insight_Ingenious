import logging
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionToolMessageParam
)
from ingenious.utils.prompt_templates import system_prompt_template, follow_up_prompt_template

logger = logging.getLogger(__name__)


def build_system_prompt(
        system_prompt: str | None = None,
        user_name: str | None = None
) -> ChatCompletionSystemMessageParam:
    # Build system prompt
    if (system_prompt is None):
        system_prompt = system_prompt_template.render(user_name=user_name)
        logger.debug(f"system_prompt:\n{system_prompt}")

    system_prompt_message: ChatCompletionSystemMessageParam = {
        "role": "system",
        "content": system_prompt
    }

    return system_prompt_message


def build_follow_up_prompt() -> ChatCompletionSystemMessageParam:
    follow_up_prompt = follow_up_prompt_template.render()
    follow_up_prompt_message: ChatCompletionSystemMessageParam = {
        "role": "system",
        "content": follow_up_prompt
    }

    return follow_up_prompt_message


def build_user_message(user_prompt: str, user_name: str | None) -> ChatCompletionUserMessageParam:
    user_message: ChatCompletionUserMessageParam = {
        "role": "user",
        "content": user_prompt
    }

    if user_name:
        user_message["name"] = user_name

    return user_message


def build_assistant_message(
        content: str | None, tool_calls: list[dict[str, object]] | None = None) -> ChatCompletionAssistantMessageParam:
    assistant_message: ChatCompletionAssistantMessageParam = {
        "role": "assistant"
    }

    if content is not None:
        assistant_message["content"] = content

    if tool_calls:
        assistant_message["tool_calls"] = tool_calls  # type: ignore

    return assistant_message


def build_tool_message(content: str, tool_call_id: str, function_name: str) -> ChatCompletionToolMessageParam:
    tool_message: ChatCompletionToolMessageParam = {
        "role": "tool",
        "content": content,
        "tool_call_id": tool_call_id,
        "name": function_name,  # type: ignore
    }

    return tool_message


def build_message(
        role: str,
        content: str | None,
        user_name: str | None = None,
        tool_calls: list[dict[str, object]] | None = None,
        tool_call_id: str | None = None,
        tool_call_function: dict[str, object] | None = None) -> ChatCompletionMessageParam:
    if role == "system":
        return build_system_prompt(system_prompt=str(content))
    elif role == "user":
        return build_user_message(str(content), user_name=user_name)
    elif role == "assistant":
        return build_assistant_message(content=content, tool_calls=tool_calls)
    elif role == "tool":
        if not tool_call_id or not tool_call_function:
            raise ValueError("Tool message requires tool_call_id and tool_call_function.")
        return build_tool_message(str(content), tool_call_id, str(tool_call_function["name"]))
    else:
        raise ValueError("Invalid message role.")
