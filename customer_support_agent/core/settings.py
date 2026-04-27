### Central configuration manager for your entire application, Control panel of your entire system

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Keep .env loading stable even when uvicorn/streamlit is launched
        # from a parent directory or a different terminal working directory.
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Copilot for Support Agents"

    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    llm_temperature: float = 0.2

    openai_api_key: str = ""
    google_api_key: str = ""
    google_embedding_model: str = "gemini-embedding-001"
    enable_local_embeddings: bool = False

    workspace_dir: Path = PROJECT_ROOT
    data_dir: Path = Path("data")
    db_path: Path = Path("data/support.db")
    chroma_rag_dir: Path = Path("data/chroma_rag")
    chroma_mem0_dir: Path = Path("data/chroma_mem0")
    knowledge_base_dir: Path = Path("knowledge_base")
    ca_bundle_path: Path = Path("cacert.pem")

    rag_chunk_size: int = 800
    rag_chunk_overlap: int = 120
    rag_top_k: int = 4
    mem0_top_k: int = 5

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    dashboard_api_url: str = "http://localhost:8000"

    def resolve(self, path: Path) -> Path:
        """Resolve relative paths against the project root."""
        return path if path.is_absolute() else self.workspace_dir / path

    @property
    def db_file(self) -> Path:
        return self.resolve(self.db_path)

    @property
    def chroma_rag_path(self) -> Path:
        return self.resolve(self.chroma_rag_dir)

    @property
    def chroma_mem0_path(self) -> Path:
        return self.resolve(self.chroma_mem0_dir)

    @property
    def knowledge_base_path(self) -> Path:
        return self.resolve(self.knowledge_base_dir)

    @property
    def ca_bundle_file(self) -> Path:
        return self.resolve(self.ca_bundle_path)

    @property
    def effective_google_embedding_model(self) -> str:
        """
        Normalize and auto-upgrade legacy embedding model IDs to a supported Gemini model.
        """
        model = (self.google_embedding_model or "").strip()
        if not model:
            return "gemini-embedding-001"

        if model.startswith("models/"):
            model = model[len("models/") :]

        deprecated_aliases = {
            "text-embedding-004",
            "embedding-001",
            "embedding-gecko-001",
            "gemini-embedding-exp",
            "gemini-embedding-exp-03-07",
        }
        if model in deprecated_aliases:
            return "gemini-embedding-001"

        return model


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    configure_ssl_cert_env(settings)
    return settings


def configure_ssl_cert_env(settings: Settings) -> None:
    """Point HTTP clients at the project CA bundle when it exists."""
    ca_bundle = settings.ca_bundle_file
    if not ca_bundle.is_file():
        return

    ca_bundle_value = str(ca_bundle)
    for env_name in ("SSL_CERT_FILE", "REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE"):
        os.environ.setdefault(env_name, ca_bundle_value)


def ensure_directories(settings: Settings | None = None) -> None:
    """Create the local directories required by SQLite and ChromaDB."""
    config = settings or get_settings()
    configure_ssl_cert_env(config)

    for path in (
        config.resolve(config.data_dir),
        config.chroma_rag_path,
        config.chroma_mem0_path,
        config.knowledge_base_path,
    ):
        path.mkdir(parents=True, exist_ok=True)
