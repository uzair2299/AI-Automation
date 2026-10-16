"""Gemini & Vertex AI foundation model provider."""
from typing import Any, Optional
from smiota.core.config import get_settings
from smiota.core.logging import logger
from smiota.core.exceptions import LLMProviderError
from smiota.llm.guardrails import SafetyGuardrails


class GeminiProvider:
    """Manages Vertex AI / Gemini LLM invocations and embeddings."""

    def __init__(self):
        self.settings = get_settings()
        self.model_name = self.settings.GEMINI_MODEL
        self.embedding_model = self.settings.GEMINI_EMBEDDING_MODEL
        self._client = None
        self._initialized = False

    def _get_vertex_client(self):
        """Lazy-initialize official Google GenAI Vertex AI client or Gemini API Key client."""
        if not self._initialized:
            self._initialized = True
            try:
                import os
                from google import genai
                api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
                if api_key:
                    self._client = genai.Client(api_key=api_key)
                    self.model_name = "gemini-1.5-flash"
                    logger.info("Initialized Google GenAI Client with GEMINI_API_KEY")
                else:
                    # Connect to Vertex AI backend on GCP using project & region
                    self._client = genai.Client(
                        vertexai=True,
                        project=self.settings.GCP_PROJECT_ID,
                        location=self.settings.GCP_REGION,
                    )
                    logger.info(
                        f"Initialized Vertex AI Client (Project: {self.settings.GCP_PROJECT_ID}, Region: {self.settings.GCP_REGION})"
                    )
            except Exception as e:
                logger.info(
                    f"Vertex AI Client running in local mock mode (GCP credentials not configured: {e})"
                )
                self._client = None
        return self._client

    async def generate_completion(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        """Call Gemini model with system instruction and safety parameters."""
        SafetyGuardrails.validate_input(prompt)
        sanitized_prompt = SafetyGuardrails.sanitize_pii(prompt)

        logger.info(f"Calling Vertex AI [{self.model_name}] (chars: {len(sanitized_prompt)})")

        client = self._get_vertex_client()
        if client:
            try:
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=sanitized_prompt,
                    config={
                        "temperature": temperature,
                        "system_instruction": system_instruction,
                    },
                )
                return response.text
            except Exception as e:
                logger.warning(f"Vertex AI call encountered error: {e}. Falling back to simulation.")

        # Local development / fallback response
        return f"[Gemini 1.5 Pro via Vertex AI] Analyzed: '{sanitized_prompt[:60]}...'"

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate vector embedding for text using text-embedding-004 on Vertex AI."""
        client = self._get_vertex_client()
        if client:
            try:
                response = client.models.embed_content(
                    model=self.embedding_model,
                    contents=text,
                )
                return response.embedding.values
            except Exception as e:
                logger.warning(f"Vertex AI embedding call failed: {e}. Falling back to zero-vector.")

        return [0.0] * 768
