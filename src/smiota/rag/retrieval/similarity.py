"""Similarity metrics, rank fusion, and diversity algorithms."""
import math

from smiota.rag.models import ScoredChunk


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two float vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    dot = sum(a * b for a, b in zip(vec_a, vec_b, strict=False))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot / (norm_a * norm_b)


def dot_product(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute dot product between two float vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    return sum(a * b for a, b in zip(vec_a, vec_b, strict=False))


def reciprocal_rank_fusion(
    dense_results: list[ScoredChunk],
    sparse_results: list[ScoredChunk],
    k: int = 60,
    dense_weight: float = 0.5,
    sparse_weight: float = 0.5,
) -> list[ScoredChunk]:
    """Combine dense vector and sparse keyword rankings using Reciprocal Rank Fusion (RRF)."""
    scores: dict[str, float] = {}
    chunk_map: dict[str, ScoredChunk] = {}

    # Accumulate dense rankings
    for rank_idx, scored in enumerate(dense_results):
        cid = scored.chunk.chunk_id
        chunk_map[cid] = scored
        scores[cid] = scores.get(cid, 0.0) + (dense_weight / (k + rank_idx + 1))

    # Accumulate sparse BM25 rankings
    for rank_idx, scored in enumerate(sparse_results):
        cid = scored.chunk.chunk_id
        if cid not in chunk_map:
            chunk_map[cid] = scored
        scores[cid] = scores.get(cid, 0.0) + (sparse_weight / (k + rank_idx + 1))

    # Sort merged results by fused RRF score descending
    sorted_items = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    fused_results: list[ScoredChunk] = []

    for rank, (cid, fused_score) in enumerate(sorted_items, start=1):
        original = chunk_map[cid]
        fused_results.append(
            ScoredChunk(
                chunk=original.chunk,
                score=fused_score,
                dense_score=original.dense_score,
                sparse_score=original.sparse_score,
                rerank_score=original.rerank_score,
                rank=rank,
            )
        )

    return fused_results


def maximal_marginal_relevance(
    query_embedding: list[float],
    candidate_chunks: list[ScoredChunk],
    top_k: int = 5,
    lambda_mult: float = 0.5,
) -> list[ScoredChunk]:
    """Maximal Marginal Relevance (MMR) for reducing redundancy while maintaining relevance."""
    if not candidate_chunks or top_k <= 0:
        return []

    if len(candidate_chunks) <= top_k:
        return candidate_chunks

    selected: list[ScoredChunk] = []
    unselected = list(candidate_chunks)

    # Precompute query similarities for all candidates
    query_sims: dict[str, float] = {
        sc.chunk.chunk_id: (
            cosine_similarity(query_embedding, sc.chunk.embedding)
            if sc.chunk.embedding
            else sc.score
        )
        for sc in unselected
    }

    while len(selected) < top_k and unselected:
        best_candidate: ScoredChunk | None = None
        best_mmr_score = -float("inf")

        for candidate in unselected:
            cid = candidate.chunk.chunk_id
            sim_to_query = query_sims[cid]

            # Max similarity to already selected chunks
            max_sim_to_selected = 0.0
            if selected and candidate.chunk.embedding:
                for sel in selected:
                    if sel.chunk.embedding:
                        sim = cosine_similarity(candidate.chunk.embedding, sel.chunk.embedding)
                        max_sim_to_selected = max(max_sim_to_selected, sim)

            mmr_score = lambda_mult * sim_to_query - (1.0 - lambda_mult) * max_sim_to_selected
            if mmr_score > best_mmr_score:
                best_mmr_score = mmr_score
                best_candidate = candidate

        if best_candidate is None:
            break

        selected.append(best_candidate)
        unselected.remove(best_candidate)

    # Re-index ranks
    for rank, item in enumerate(selected, start=1):
        item.rank = rank

    return selected
