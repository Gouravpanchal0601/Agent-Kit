def info_agent(message: str):
    # Simulated database or doc search
    if "warranty" in message.lower():
        return "Our warranty lasts 12 months from the date of purchase."
    elif "delivery" in message.lower():
        return "Delivery usually takes 3–5 business days."
    else:
        return "Can you clarify what information you need?"
