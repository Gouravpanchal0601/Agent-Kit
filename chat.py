import os
import requests
import openai
from typing import List

OPENAI_API_KEY = "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"
SERPAPI_API_KEY = "146b7ca7512eb443a142787c699bb201d9bdc5194edb0b1cd8763bb3aa75edf9"

openai.api_key = OPENAI_API_KEY


def web_search(query: str, num_results: int = 5) -> List[str]:
    """
    Performs a web search using SerpAPI and returns text snippets.
    """
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "engine": "google",
        "num": num_results,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    results = []
    for item in data.get("organic_results", []):
        snippet = item.get("snippet")
        link = item.get("link")
        if snippet and link:
            results.append(f"{snippet} (Source: {link})")

    return results

def ai_web_agent(question: str) -> str:

    search_results = web_search(question)

    if not search_results:
        return "No relevant web results found."

    context = "\n".join(search_results)

    prompt = f"""
You are an AI assistant that answers questions using web search results.

Question:
{question}

Web Search Results:
{context}

Instructions:
- Use only the information from the web results
- Be clear and concise
- Cite sources inline when relevant

Answer:
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful web research assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    return response["choices"][0]["message"]["content"]


if __name__ == "__main__":
    print("=== AI Web Search Agent ===")
    while True:
        user_input = input("\nAsk a question (or type 'exit'): ")
        if user_input.lower() == "exit":
            break

        answer = ai_web_agent(user_input)
        print("\nAnswer:\n")
        print(answer)
