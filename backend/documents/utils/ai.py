import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

def generate_ai_clause(prompt: str, context: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant that generates NDA clauses. Generate a clause based on the provided context and prompt."},
            {"role": "user", "content": f"Context:\n{context}\n\nPrompt:\n{prompt}"}
        ],
    )
    return response.choices[0].message['content']
