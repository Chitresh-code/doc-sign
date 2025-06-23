import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

def summarize_encrypted_html(html_content: str) -> dict:
    system_msg = (
        "You are an assistant that summarizes encrypted HTML legal/business documents "
        "and extracts structured summaries for easy review."
    )

    prompt = f"""
    Below is an encrypted HTML document.

    Extract and return a structured JSON object with the following fields:
    - "terms": A brief explanation of the main agreement or legal terms.
    - "responsibilities": What each party is expected to do or avoid.
    - "dates": Important dates such as effective date, expiration, or signing date.
    - "signatures_required": Names or roles of signers required for this document.

    If any field is missing from the document, leave it as null or an empty string.

    ### ENCRYPTED HTML:
    {html_content}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    import json
    content = response.choices[0].message['content']

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"error": "AI returned non-JSON content", "raw": content}