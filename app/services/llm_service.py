import os
import time
import random
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

    def _generate_with_retry(self, prompt: str, fallback_message: str, component: str = "LLMService") -> str:
        max_retries = 2
        base_delay = 1.0
        
        for attempt in range(max_retries + 1):
            try:
                response = self.client.models.generate_content(model=self.model_name, contents=prompt)
                
                # Safe response parsing
                if not response:
                    logger.error(f"[{component}] Attempt {attempt+1}/{max_retries+1}: Empty response object from Gemini.")
                    if attempt == max_retries: return fallback_message
                    continue
                    
                # Handle google-genai response structure safely
                try:
                    text = response.text
                    if text:
                        return text
                    logger.error(f"[{component}] Attempt {attempt+1}/{max_retries+1}: Gemini returned a response but response.text is empty.")
                    if attempt == max_retries: return fallback_message
                except Exception as parse_e:
                    logger.error(f"[{component}] Attempt {attempt+1}/{max_retries+1}: Failed to extract text from response. {type(parse_e).__name__}: {str(parse_e)}")
                    if attempt == max_retries: return fallback_message
                    
            except Exception as e:
                error_str = str(e)
                error_type = type(e).__name__
                # Check for transient errors: 429 or 5xx
                if any(code in error_str for code in ["429", "500", "502", "503", "504"]):
                    if attempt < max_retries:
                        delay = (base_delay * (2 ** attempt)) + random.uniform(0.1, 0.5)
                        logger.warning(f"[{component}] Transient error ({error_type}). Retrying in {delay:.2f}s (Attempt {attempt+1}/{max_retries})")
                        time.sleep(delay)
                        continue
                logger.error(f"[{component}] Permanent API Error ({error_type}): {error_str} [Model: {self.model_name}]")
                return fallback_message
        return fallback_message

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
        
        return self._generate_with_retry(prompt, "AI insights are temporarily unavailable. Your analysis results are unaffected.", component="ReportGeneration")
            
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
        
        return self._generate_with_retry(prompt, "Comparison insights are temporarily unavailable.", component="CompareGeneration")

    def generate_assistant_response(self, prompt: str) -> str:
        if not self.client:
            return "AI Assistant is currently offline. Please configure your GEMINI_API_KEY."
        return self._generate_with_retry(prompt, "The AI assistant is temporarily busy. Please try again in a moment.", component="Assistant")

llm_service = LLMService()
