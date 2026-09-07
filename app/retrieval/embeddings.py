from __future__ import annotations

from functools import lru_cache
from dotenv import load_dotenv
load_dotenv()
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from app.retrieval.config import retrieval_config

@lru_cache(maxsize=1)
def get_embedding_model() -> OpenAIEmbeddings:
    """
    Create and cache the embedding model.

    @lru_cache ensures we do not reload the model every time
    the retrieval pipeline is used.
    """
#     embeddings = GoogleGenerativeAIEmbeddings(
#     model="gemini-embedding-001"
# )
    # model = OpenAIEmbeddings(
    #     model = retrieval_config.embedding_model,
    # )

    model = HuggingFaceEmbeddings(
        model=retrieval_config.embedding_model,
        model_kwargs={
            "device": "cpu",
        },
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )

    return model