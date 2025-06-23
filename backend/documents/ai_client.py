import openai

def generate_nda_terms(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a legal document assistant."},
            {"role": "user", "content": f"Generate key clauses for an NDA. Description: {prompt}"}
        ],
        max_tokens=700
    )
    return response['choices'][0]['message']['content']