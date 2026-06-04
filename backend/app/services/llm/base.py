from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    async def generate_report(
        self,
        condition: str,
        confidence: float,
        severity: str,
        user_profile: dict = None,
    ) -> str:
        """Generates a personalized skincare report."""
        pass

    @abstractmethod
    async def chat(self, user_message: str, scan_context: dict) -> str:
        """Handles chat interaction regarding a scan."""
        pass
