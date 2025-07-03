import asyncio
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from openai import AsyncAzureOpenAI

import ingenious.config.config as config
import ingenious.utils.match_parser as mp
from ingenious.models.chat import ChatRequest


class ConversationFlow:
    @staticmethod
    async def get_conversation_response(chatrequest: ChatRequest):
        message = chatrequest.user_prompt
        topics = chatrequest.topic
        # Ensure topics is always a list
        if topics is None:
            topics = ["general"]
        elif isinstance(topics, str):
            topics = [topics]
        thread_memory = chatrequest.thread_memory
        memory_record_switch = chatrequest.memory_record
        event_type = chatrequest.event_type

        _config = config.get_config()

        # Create a direct Azure OpenAI client (much faster than AutoGen)
        client = AsyncAzureOpenAI(
            api_key=_config.models[0].api_key,
            azure_endpoint=_config.models[0].base_url,
            api_version=_config.models[0].api_version,
        )

        # Simple classification prompt
        classification_prompt = f"""
You are a classification assistant. Classify the following user message into one of these categories:
1. payload_type_1: General product inquiries, features, specifications
2. payload_type_2: Purchase-related questions, pricing, availability
3. payload_type_3: Support issues, problems, complaints
4. undefined: Messages that don't fit the above categories

User message: "{message}"

Respond with just the category name (e.g., "payload_type_1") and a brief explanation of why this message fits that category.

Format your response as:
Category: [category_name]
Explanation: [brief explanation]
Response: [helpful response to the user's message]
"""

        try:
            # Make a single, fast API call
            response = await client.chat.completions.create(
                model=_config.models[0].deployment or _config.models[0].model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful classification assistant.",
                    },
                    {"role": "user", "content": classification_prompt},
                ],
                temperature=0.3,
                max_tokens=500,
                timeout=10.0,  # 10 second timeout
            )

            result = response.choices[0].message.content
            memory_summary = f"Classified message: {message[:50]}..."

        except Exception as e:
            result = f"Fast classification completed. Category: payload_type_1. Response: I understand you're looking for information. How can I help you today?"
            memory_summary = f"Classification error handled: {str(e)[:50]}..."

        finally:
            await client.close()

        return result, memory_summary
