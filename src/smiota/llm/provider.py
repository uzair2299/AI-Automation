"""Gemini & Vertex AI foundation model provider."""
from typing import Any, Optional
import json
import os
import tempfile
from smiota.core.config import get_settings
from smiota.core.logging import logger
from smiota.core.exceptions import LLMProviderError
from smiota.llm.guardrails import SafetyGuardrails


def _ensure_gcp_credentials() -> Optional[str]:
    """Ensure Google Cloud Application Credentials are validly set up.

    Supports:
    1. Local Windows file path: GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\key.json
    2. Docker / Railway file path: GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcp_creds.json
    3. Railway / Cloud raw JSON environment variable:
       - GOOGLE_APPLICATION_CREDENTIALS_JSON or GCP_SERVICE_ACCOUNT_KEY or GOOGLE_CREDENTIALS
       - Or if user pasted raw JSON directly into GOOGLE_APPLICATION_CREDENTIALS
       Writes the JSON to /tmp/gcp_creds.json (or OS temp dir) and sets GOOGLE_APPLICATION_CREDENTIALS.
    4. Auto-detecting gcloud Application Default Credentials on Windows if not explicitly set.
    """
    creds_val = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    raw_json_candidate = (
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        or os.environ.get("GCP_SERVICE_ACCOUNT_KEY")
        or os.environ.get("GOOGLE_CREDENTIALS")
    )

    # In Linux container, standard path is /tmp/gcp_creds.json; on Windows, use system tempdir
    target_path = "/tmp/gcp_creds.json" if os.name != "nt" else os.path.join(tempfile.gettempdir(), "gcp_creds.json")

    # Case A: User set GOOGLE_APPLICATION_CREDENTIALS_JSON with raw JSON string
    if raw_json_candidate:
        try:
            parsed = json.loads(raw_json_candidate.strip())
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(parsed, f)
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = target_path
            logger.info(f"Loaded GCP credentials from JSON environment variable and saved to {target_path}")
            return target_path
        except Exception as e:
            logger.warning(f"Failed to parse GCP credentials from JSON environment variable: {e}")

    # Case B: User pasted raw JSON directly into GOOGLE_APPLICATION_CREDENTIALS
    if creds_val and creds_val.strip().startswith("{"):
        try:
            parsed = json.loads(creds_val.strip())
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(parsed, f)
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = target_path
            logger.info(f"Extracted raw JSON from GOOGLE_APPLICATION_CREDENTIALS and saved to {target_path}")
            return target_path
        except Exception as e:
            logger.warning(f"Failed to parse raw JSON from GOOGLE_APPLICATION_CREDENTIALS: {e}")

    # Case C: GOOGLE_APPLICATION_CREDENTIALS points to an existing file
    if creds_val and os.path.exists(creds_val):
        logger.info(f"Using Google Cloud credentials file from {creds_val}")
        return creds_val

    # Case D: On Windows, auto-detect gcloud CLI application default credentials if not specified
    if not creds_val:
        appdata = os.environ.get("APPDATA")
        if appdata:
            gcloud_adc = os.path.join(appdata, "gcloud", "application_default_credentials.json")
            if os.path.exists(gcloud_adc):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcloud_adc
                logger.info(f"Auto-detected local gcloud credentials at {gcloud_adc}")
                return gcloud_adc

    return creds_val


class GeminiProvider:
    """Manages Vertex AI / Gemini LLM invocations and embeddings."""

    def __init__(self):
        self.settings = get_settings()
        self.embedding_model = getattr(self.settings, "GEMINI_EMBEDDING_MODEL", "text-embedding-004")
        self._client = None

    @property
    def model_name(self) -> str:
        return os.environ.get("GEMINI_MODEL") or getattr(self.settings, "GEMINI_MODEL", "gemini-2.5-flash") or "gemini-2.5-flash"

    @property
    def project_id(self) -> str:
        return os.environ.get("GCP_PROJECT_ID") or getattr(self.settings, "GCP_PROJECT_ID", "vertex-ai-510710") or "vertex-ai-510710"

    @property
    def location(self) -> str:
        return os.environ.get("GCP_REGION") or getattr(self.settings, "GCP_REGION", "us-central1") or "us-central1"

    def _get_vertex_client(self):
        """Lazy-initialize official Google GenAI Vertex AI client or Gemini API Key client."""
        if self._client is None:
            try:
                from google import genai

                # Automatically prepare GCP service account credentials if available
                _ensure_gcp_credentials()

                api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
                if api_key:
                    self._client = genai.Client(api_key=api_key)
                    logger.info("Initialized Google GenAI Client with GEMINI_API_KEY")
                else:
                    # Connect to Vertex AI backend on GCP using project & region
                    self._client = genai.Client(
                        vertexai=True,
                        project=self.project_id,
                        location=self.location,
                    )
                    logger.info(
                        f"Initialized Vertex AI Client (Project: {self.project_id}, Region: {self.location}, Model: {self.model_name})"
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

        # Local development / fallback response without leaking debug strings
        logger.info(f"Using graceful concierge fallback response for prompt: {sanitized_prompt[:60]}")
        return (
            "I'm here to assist you with your Smiota smart locker! "
            "I can help you check deliveries, retrieve your pickup PIN, or look up locker location and hours. "
            "How can I help you today?"
        )

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
