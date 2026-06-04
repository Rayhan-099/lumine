from .base import LLMProvider
import openai
from app.core.config import settings
import os


class OpenAIProvider(LLMProvider):
    def __init__(self):
        # Allow missing key for local dev mock fallback if not provided
        self.api_key = os.getenv("OPENAI_API_KEY", "mock-key")
        if self.api_key != "mock-key":
            openai.api_key = self.api_key

    async def generate_report(
        self,
        condition: str,
        confidence: float,
        severity: str,
        user_profile: dict = None,
    ) -> str:
        if self.api_key == "mock-key":
            return f"Mock AI Recommendation: Use a gentle cleanser and SPF 50 sunscreen daily. Your {condition} ({severity}) indicates you should focus on hydration."

        prompt = f"""
        Act as an expert dermatologist AI assistant.
        The computer vision model has detected {condition} with {confidence*100:.1f}% confidence.
        The severity is classified as {severity}.
        
        Generate a personalized, empathetic, and professional skincare report.
        Include:
        1. A brief explanation of what the condition is.
        2. Recommended ingredients to look for.
        3. Ingredients to avoid.
        4. A suggested daily routine.
        
        Add a medical disclaimer that this is an AI analysis and not a substitute for professional medical advice.
        """

        try:
            # Using async wrapper if available or sync for now (OpenAI python client 1.x supports async)
            # For simplicity, we use the synchronous call inside a thread or just the async client
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key)

            response = await client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are Lumine, an expert AI dermatology assistant.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=500,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM Error: {e}")
            return "Failed to generate report. Please try again later."

    async def chat(self, user_message: str, scan_context: dict) -> str:
        if self.api_key == "mock-key":
            return "This is a mock chat response. Please provide an OPENAI_API_KEY for real responses."

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key)

            context_str = f"Last Scan: {scan_context.get('condition')}, Severity: {scan_context.get('severity')}"

            response = await client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are Lumine, an expert AI dermatology assistant. Context: {context_str}",
                    },
                    {"role": "user", "content": user_message},
                ],
                temperature=0.7,
                max_tokens=300,
            )
            return response.choices[0].message.content
        except Exception as e:
            return "Sorry, I am currently unable to process your message."
