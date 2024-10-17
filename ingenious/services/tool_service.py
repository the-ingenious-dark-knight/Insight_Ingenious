import json
from ingenious.external_services.search_service import AzureSearchService
from ingenious.models.chat import Action, KnowledgeBaseLink, Product
from ingenious.models.tool_call_result import (ToolCallResult, ActionToolCallResult,
                                         KnowledgeBaseToolCallResult, ProductToolCallResult)
from openai.types.chat import ChatCompletionToolParam, ChatCompletionMessageToolCall


class ToolService:
    def __init__(self, search_services: dict[str, AzureSearchService]):
        self.search_services = search_services

    async def execute_tool_call(self, tool_call: ChatCompletionMessageToolCall) -> ToolCallResult:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        if function_name == "search_products":
            return await self._handle_search_products(function_args)
        elif function_name == "search_knowledge_base":
            return await self._handle_search_knowledge_base(function_args)
        elif function_name == "suggest_action":
            return await self._handle_suggest_action(function_args)
        else:
            raise ValueError(f"Unknown function name: {function_name}")

    async def _handle_search_products(self, function_args: dict) -> ProductToolCallResult:
        results = await self.search_services["products"].search(
            function_args.get("query"),
            function_args.get("top", 3))
        products = [Product(sku=str(result.get("code"))) for result in results or []]
        return ProductToolCallResult(results=json.dumps(results), products=products)

    async def _handle_search_knowledge_base(self, function_args: dict) -> KnowledgeBaseToolCallResult:
        results = await self.search_services["knowledge_base"].search(
            function_args.get("query"),
            function_args.get("top", 1))
        knowledge_base_links = [
            KnowledgeBaseLink(
                title=str(result.get("Title")),
                url=str(result.get("Permalink"))) for result in results or []]
        return KnowledgeBaseToolCallResult(results=json.dumps(results), knowledge_base_links=knowledge_base_links)

    async def _handle_suggest_action(self, function_args: dict) -> ActionToolCallResult:
        result = str(function_args.get("action"))
        actions = [Action(action=result)]
        return ActionToolCallResult(results=json.dumps({"action": result}), actions=actions)

    @staticmethod
    def get_tool_definitions() -> list[ChatCompletionToolParam]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "suggest_action",
                    "description": "Suggest an action to the user based on the user's latest prompt.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "The action to suggest to the user",
                                "enum": ["you_should_google_it", "try_asking_a_friend", "go_touch_grass"],  # noqa: E501
                            },
                        },
                        "required": ["action"],
                    },
                }
            }
        ]
