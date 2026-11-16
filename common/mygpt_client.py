"""Small MyGPT REST client shared by the workshop notebooks and scripts.

Endpoints and payloads follow the MyGPT developer guide:
https://github.com/stjude/MyGPT/blob/main/development.md
and the reference client at MyGPT/scripts/python_api_client.py.

Usage
-----
    from common.mygpt_client import MyGPTClient
    client = MyGPTClient.from_env()          # reads .env at the repo root
    client.list_datasets()
    result = client.ask("Do glioblastoma tumors have a high degree of lymphocyte infiltration?")
    result["answer"], result["QRS"], result["ARS"], result["HI"]
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "workshop_outputs"

try:  # python-dotenv is optional at import time
    from dotenv import load_dotenv

    load_dotenv(REPO_ROOT / ".env")
except ImportError:  # pragma: no cover
    pass

# Same prompt shape as MyGPT/scripts/python_api_client.py
RAG_PROMPT = (
    "### INSTRUCTIONS ###\n"
    "Use the following context from the user's documents to answer the question. "
    "If the context does not contain the answer, say that the library does not contain it.\n\n"
    "### CONTEXT ###\n{context}\n\n"
    "### QUESTION ###\n{question}\n\n"
    "### ANSWER ###\n"
)


def outputs_dir() -> Path:
    """Return workshop_outputs/, creating it if needed."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    return OUTPUT_DIR


class MyGPTClient:
    """Thin wrapper around the MyGPT Django REST API."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        dataset: str = "",
        llm: str = "llama3:latest",
        embedding_model: str = "nomic-embed-text:latest",
        user_email: str = "",
        ollama_url: str = "http://localhost:11434",
        timeout: int = 300,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.dataset = dataset
        self.llm = llm
        self.embedding_model = embedding_model
        self.user_email = user_email
        self.ollama_url = ollama_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.access_token: str | None = None

    # ------------------------------------------------------------------ setup
    @classmethod
    def from_env(cls, authenticate: bool = True) -> "MyGPTClient":
        """Build a client from environment variables / .env (see .env.example)."""
        env = os.environ.get
        client = cls(
            base_url=env("MYGPT_BASE_URL", "http://localhost:8000"),
            dataset=env("MYGPT_DATASET", ""),
            llm=env("MYGPT_LLM", "llama3:latest"),
            embedding_model=env("MYGPT_EMBEDDING_MODEL", "nomic-embed-text:latest"),
            user_email=env("MYGPT_USER_EMAIL", ""),
            ollama_url=env("OLLAMA_URL", "http://localhost:11434"),
        )
        user, password = env("MYGPT_USERNAME"), env("MYGPT_PASSWORD")
        if authenticate and user and password:
            client.authenticate(user, password)
        return client

    def authenticate(self, username: str, password: str) -> None:
        """Get a JWT access token from POST /token/."""
        res = self.session.post(
            f"{self.base_url}/token/",
            json={"username": username, "password": password},
            timeout=30,
        )
        res.raise_for_status()
        self.access_token = res.json().get("access")

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def _post(self, path: str, payload: dict[str, Any]) -> Any:
        res = self.session.post(
            f"{self.base_url}{path}", json=payload, headers=self._headers(), timeout=self.timeout
        )
        res.raise_for_status()
        return res.json()

    # ---------------------------------------------------------------- library
    def list_datasets(self) -> list[dict[str, Any]]:
        """POST /api/get_datasets/ — libraries visible to this user."""
        return self._post("/api/get_datasets/", {"user_email": self.user_email, "user_group": ""})

    def get_dataset_details(self, dataset: str | None = None) -> dict[str, Any]:
        """POST /api/get_dataset_details/ — settings and weights of one library."""
        return self._post(
            "/api/get_dataset_details/",
            {"dataset": dataset or self.dataset, "user_email": self.user_email, "user_group": ""},
        )

    def get_documents(self, dataset: str | None = None) -> dict[str, Any]:
        """POST /api/get_documents/ — documents in a library."""
        return self._post(
            "/api/get_documents/",
            {"dataset": dataset or self.dataset, "user_email": self.user_email, "user_group": ""},
        )

    def update_dataset(self, dataset: str | None = None, **fields: Any) -> dict[str, Any]:
        """POST /api/update_dataset/ — e.g. Qsem_a=4, Qkey_b=-4, QRS_p=1, ARS_q=2."""
        return self._post("/api/update_dataset/", {"dataset": dataset or self.dataset, **fields})

    # -------------------------------------------------------------- retrieval
    def get_context(
        self,
        question: str,
        dataset: str | None = None,
        max_chunks: int = 5,
        use_default_qrs: bool = True,
        question_best_distance: float = 0.2,
        question_worst_distance: float = 1.7,
        no_cutoff: bool = False,
    ) -> dict[str, Any]:
        """POST /api/get_context/ — retrieve chunks and the question relevance score (QRS)."""
        return self._post(
            "/api/get_context/",
            {
                "text": question,
                "dataset": dataset or self.dataset,
                "model_type": self.llm,
                "use_default_qrs": use_default_qrs,
                "question_best_distance": question_best_distance,
                "question_worst_distance": question_worst_distance,
                "maximum_chunks_count": max_chunks,
                "no_cutoff": no_cutoff,
                "new_conversation": True,
                "previous_query": "",
                "no_context": False,
                "selected_embedding_model": self.embedding_model,
            },
        )

    def generate(self, prompt: str, temperature: float = 0.3, model: str | None = None) -> str:
        """POST /api/ollama_generate/ — generation through the MyGPT backend."""
        data = self._post(
            "/api/ollama_generate/",
            {"model": model or self.llm, "prompt": prompt, "temperature": temperature, "stream": False},
        )
        return data.get("response", "")

    def score_answer(
        self,
        question: str,
        answer: str,
        dataset: str | None = None,
        QRS_p: float = 1,
        ARS_q: float = 2,
        temperature: float = 0.3,
    ) -> dict[str, Any]:
        """POST /api/save_answer/ — store the answer and get ARS and the hallucination index (HI).

        Call get_context() for the same question first: MyGPT scores the answer against
        the chunks it retrieved for that question.
        """
        return self._post(
            "/api/save_answer/",
            {
                "question_text": question,
                "answer_text": answer,
                "answer_no_context_text": "n/a",
                "model_type": self.llm,
                "dataset": dataset or self.dataset,
                "no_context": False,
                "use_default_ars": True,
                "answer_best_distance": 0.12,
                "answer_worst_distance": 1.42,
                "QRS_p": QRS_p,
                "ARS_q": ARS_q,
                "use_default_hi": True,
                "temperature": temperature,
                "top_k": 20,
                "top_p": 0.7,
            },
        )

    def ask(self, question: str, dataset: str | None = None, max_chunks: int = 5, score: bool = True) -> dict[str, Any]:
        """Full RAG round trip: retrieve → generate → (optionally) score.

        Returns a flat dict that is convenient for building a pandas DataFrame.
        """
        ctx = self.get_context(question, dataset=dataset, max_chunks=max_chunks)
        sources = ctx.get("sources", []) or []
        context_text = (ctx.get("context") or "").strip()
        if not context_text and sources:
            context_text = "\n\n---\n\n".join(s.get("context", "") for s in sources[:max_chunks])
        if not context_text:
            context_text = "No document context available."

        answer = self.generate(RAG_PROMPT.format(context=context_text, question=question))
        row: dict[str, Any] = {
            "question": question,
            "answer": answer.strip(),
            "context": context_text,
            "n_sources": len(sources),
            "QRS": ctx.get("relevance_score"),
            "Qsem": ctx.get("semantic_score"),
            "Qkey": ctx.get("keyword_score"),
            "Qrank": ctx.get("rerank_score"),
        }
        if score:
            s = self.score_answer(question, row["answer"], dataset=dataset)
            row.update(
                {
                    "ARS": s.get("relevance_score"),
                    "Asem": s.get("semantic_score"),
                    "Akey": s.get("keyword_score"),
                    "HI": s.get("hallucination_index_by_ml"),
                    "HI_ml": s.get("hallucination_index_by_ml"),
                    "HI_equation": s.get("hallucination_index_by_equation"),
                }
            )
        return row

    # ------------------------------------------------------- direct Ollama use
    def ollama(self, prompt: str, model: str | None = None, temperature: float = 0.0, json_mode: bool = False) -> str:
        """Call Ollama's /api/generate directly (question generation, LLM judge)."""
        payload: dict[str, Any] = {
            "model": model or self.llm,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if json_mode:
            payload["format"] = "json"
        res = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=self.timeout)
        res.raise_for_status()
        return res.json().get("response", "")


# ------------------------------------------------------------ fallback data
FALLBACK_URL = (
    "https://raw.githubusercontent.com/stjude/MyGPT-evaluations/main/PubMedQA/outputs/answers/"
    "answers-gpt-oss-20b-PubMedQA-nomic-rerank-full.csv"
)


def load_fallback_pubmedqa():
    """Download (once) and return the scored PubMedQA run from MyGPT-evaluations (GPL-3.0).

    The file is cached in data/fallback/ (ignored by Git) rather than redistributed here.
    """
    import pandas as pd

    cache = REPO_ROOT / "data" / "fallback" / "pubmedqa_scored.csv"
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        res = requests.get(FALLBACK_URL, timeout=60)
        res.raise_for_status()
        cache.write_bytes(res.content)
    return pd.read_csv(cache)
