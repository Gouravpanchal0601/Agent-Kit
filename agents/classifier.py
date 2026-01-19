
from openai import OpenAI

client = OpenAI(api_key="")

def classify_intent(message: str):
    prompt = f"""
    You are an intent classifier for support chats.
    Detect intent from this user message and return only one word: REFUND, INFO, ESCALATE, GENERAL
    User: "{message}"
    """
    try:
        resp = client.responses.create(
            model="gpt-4o-mini",
            input=prompt
        )
        # Make sure to extract text correctly
        intent_text = resp.output_text.strip().upper()
        if intent_text not in ["REFUND", "INFO", "ESCALATE"]:
            return "GENERAL"
        return intent_text
    except Exception as e:
        print("Classifier error:", e)
        return "GENERAL"
