import os
import google.generativeai as genai
from app.core.logging import logger

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None

    def generate_report(self, prediction: dict, text_analysis: dict, user_context: list = None, user_description: str = "") -> str:
        if not self.model:
            return "AI Insights are currently disabled. Please configure your GEMINI_API_KEY in the .env file."
        
        prompt = f"""
        You are Lumine AI, an intelligent, empathetic digital skin health assistant.
        A user has requested an analysis.
        
        User's provided symptoms/description: {user_description}
        Model Prediction: {prediction}
        Condition Details: {text_analysis}
        """
        
        if user_context and len(user_context) > 0:
            prompt += f"\nHistorical Scan Context (last 5 scans): {user_context}\n"
            prompt += "Acknowledge their history (e.g., 'This is the 2nd time we've seen this') if relevant, but do not invent trends."
            
        prompt += """
        Provide a short (3-4 sentences) explanation of what these results might mean, 
        and give 2 practical skincare tips. 
        Remember, you are an informational assistant, not a doctor. Use a calm, premium tone.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API Error in generate_report: {e}")
            return f"AI insights are temporarily unavailable. Your analysis results are unaffected."
            
    def generate_comparison(self, a1_data: dict, a2_data: dict) -> str:
        if not self.model:
            return "Comparison insights are currently disabled. Please configure your GEMINI_API_KEY."
            
        prompt = f"""
        You are Lumine AI, an intelligent skin health assistant.
        The user is comparing two past skin analyses.
        
        Analysis 1 (Older): {a1_data}
        Analysis 2 (Newer): {a2_data}
        
        Provide a concise, 2-3 sentence summary comparing the two. Note if the condition seems to be changing, improving, or remaining the same based purely on the provided data. Do not diagnose.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API Error in generate_comparison: {e}")
            return "Comparison insights are temporarily unavailable."

    def generate_assistant_response(self, prompt: str) -> str:
        if not self.model:
            return "AI Assistant is currently offline. Please configure your GEMINI_API_KEY."
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API Error in generate_assistant_response: {e}")
            return "I'm sorry, I couldn't process your request right now due to a service interruption."

llm_service = LLMService()
