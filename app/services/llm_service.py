import os
from google import genai
from app.core.logging import logger

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def check_llm_status(self):
        if not self.client:
            logger.warning("LLM Diagnostics: GEMINI_API_KEY is missing. AI insights are disabled.")
            return
        
        logger.info(f"LLM Diagnostics: GEMINI_MODEL configured as '{self.model_name}'")
        try:
            # A lightweight initialization test to check if the model is reachable
            response = self.client.models.generate_content(
                model=self.model_name,
                contents="ping"
            )
            logger.info("LLM Diagnostics: Gemini inference provider initialized and reachable.")
        except Exception as e:
            logger.error(f"LLM Diagnostics: Gemini model unavailable or initialization failed. Exception: {type(e).__name__} - {str(e)}")

    def generate_report(self, prediction: dict, text_analysis: dict, user_context: list = None, user_description: str = "") -> str:
        if not self.client:
            return "AI Insights are currently disabled. Please configure your GEMINI_API_KEY in the .env file."
        
        prompt = f"""
        You are Lumine AI, an intelligent, empathetic digital skin health assistant.
        A user has requested an analysis. 
        
        Please interpret the following structured data.
        
        [MODEL_VISUAL_CLASSIFICATION]: {prediction.get("predicted_label", "Unknown")}
        [MODEL_SCORE]: {prediction.get("confidence", "Unknown")}%
        [USER_REPORTED_SYMPTOMS]: {user_description if user_description else "None provided"}
        [EDUCATIONAL_METADATA]: {text_analysis}
        """
        
        if user_context and len(user_context) > 0:
            prompt += f"\n[HISTORY_CONTEXT] (last 5 scans): {user_context}\n"
        
        prompt += """
        CRITICAL RULES:
        1. NEVER claim the user reported something that is absent from [USER_REPORTED_SYMPTOMS]. If it says "None provided", do not invent symptoms like redness or itching.
        2. NEVER convert the model classification into a definitive medical diagnosis. Use wording like "The model's top visual match is..." or "This visually aligns with...".
        3. NEVER interpret the [MODEL_SCORE] as a probability that the user actually has the disease. It is just the model's visual confidence score.
        4. Distinguish clearly between what the model detected and what the user reported.
        5. If history is provided, describe it as past model classifications (e.g., "A previous scan returned X as its top visual match"), never as past medical diagnoses.

        Provide a short (3-4 sentences) explanation of what these results might mean educationally, 
        and give 2 practical skincare tips based on the [EDUCATIONAL_METADATA]. 
        Remember, you are an informational assistant, not a doctor. Use a calm, premium tone.
        """
        
        try:
            response = self.client.models.generate_content(model=self.model_name, contents=prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API Error in generate_report: {e}")
            return f"AI insights are temporarily unavailable. Your analysis results are unaffected."
            
    def generate_comparison(self, a1_data: dict, a2_data: dict) -> str:
        if not self.client:
            return "Comparison insights are currently disabled. Please configure your GEMINI_API_KEY."
            
        prompt = f"""
        You are Lumine AI, an intelligent skin health assistant.
        The user is comparing two past skin analyses.
        
        Analysis 1 (Older): {a1_data}
        Analysis 2 (Newer): {a2_data}
        
        CRITICAL RULES:
        1. NEVER convert the model classifications into a definitive medical diagnosis.
        2. These are visual classification scores, NOT medical diagnoses. 
        
        Provide a concise, 2-3 sentence summary comparing the two. Note if the model's visual match confidence seems to be changing. Do not diagnose.
        """
        
        try:
            response = self.client.models.generate_content(model=self.model_name, contents=prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API Error in generate_comparison: {e}")
            return "Comparison insights are temporarily unavailable."

    def generate_assistant_response(self, prompt: str) -> str:
        if not self.client:
            return "AI Assistant is currently offline. Please configure your GEMINI_API_KEY."
        try:
            response = self.client.models.generate_content(model=self.model_name, contents=prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API Error in generate_assistant_response: {e}")
            return "I'm sorry, I couldn't process your request right now due to a service interruption."

llm_service = LLMService()
