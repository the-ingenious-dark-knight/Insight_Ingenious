# with the guardrails client
import guardrails as gr

gr.settings.use_server = True
guard = gr.Guard(name='two-word-guard')
guard.validate('this is more than two words')

# or with the openai sdk
# import openai
# openai.base_url = "http://localhost:8000/guards/two-word-guard/openai/v1/"
# os.environ["OPENAI_API_KEY"] = "youropenaikey"
#
# messages = [
#         {
#             "role": "user",
#             "content": "tell me about an apple with 3 words exactly",
#         },
#     ]
#
# completion = openai.chat.completions.create(
#     model="gpt-4o-mini",
#     messages=messages,
# )