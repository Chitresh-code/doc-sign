from openai import OpenAI
from django.conf import settings
import markdown as md

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_ai_clause(prompt: str, context: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that generates NDA clauses. Generate a clause based on the provided context and prompt."},
            {"role": "user", "content": f"Context:\n{context}\n\nPrompt:\n{prompt}"}
        ],
    )
    result = response.choices[0].message.content
    return md.markdown(result).strip()
