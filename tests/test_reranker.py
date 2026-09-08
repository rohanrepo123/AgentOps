from unittest.mock import Mock, patch

from app.retrieval.reranker import DocumentReranker
from app.retrieval.schemas import RetrievalResult


def make_result(doc_id: str, score: float) -> RetrievalResult:
    return RetrievalResult(
        content=f"content for {doc_id}",
        score=score,
        document_id=doc_id,
        source=f"{doc_id}.md",
        category="service",
        document_type="service",
    )


@patch("app.retrieval.reranker.CrossEncoder")
def test_reranker_sorts_by_cross_encoder_score(mock_encoder):
    model = Mock()
    model.predict.return_value = [0.1, 0.9, 0.3]
    mock_encoder.return_value = model

    reranker = DocumentReranker("test-model")
    results = reranker.rerank(
        "payment failures",
        [make_result("A", 0.2), make_result("B", 0.1), make_result("C", 0.3)],
        top_k=2,
    )

    assert [r.document_id for r in results] == ["B", "C"]
    assert results[0].reranker_score == 0.9
    assert results[0].score == 0.1
