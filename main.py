from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

from agents.guardrails import guardrails_check
from agents.classifier import classify_intent
from agents.refund_agent import refund_agent
from agents.info_agent import info_agent

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return FileResponse("static/chat.html")

@app.post("/query")
async def handle_query(req: Request):
    data = await req.json()
    user_msg = data.get("message", "")

    safe, reason = guardrails_check(user_msg)
    if not safe:
        return JSONResponse({"response": reason})

    intent = classify_intent(user_msg)

    if "REFUND" in intent:
        reply = refund_agent(user_msg)
    elif "INFO" in intent:
        reply = info_agent(user_msg)
    elif "ESCALATE" in intent:
        reply = "This issue needs human review. Forwarding to support team."
    else:
        reply = "I’m here to help! Could you tell me more about your request?"

    return JSONResponse({"response": reply, "intent": intent})
