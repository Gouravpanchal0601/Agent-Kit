def guardrails_check(message: str):
    blocked_words = ["idiot", "stupid", "hate"]
    for word in blocked_words:
        if word in message.lower():
            return False, "Your message violates our community rules."
    return True, None
