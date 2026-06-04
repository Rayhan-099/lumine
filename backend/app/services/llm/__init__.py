from .openai_provider import OpenAIProvider


# In a production setting, this could be driven by configuration
# to switch between Claude, Gemini, or OpenAI.
def get_llm_provider():
    return OpenAIProvider()
