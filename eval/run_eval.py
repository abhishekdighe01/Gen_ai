"""
Day 8 S2 — RAG Evaluation & Configuration Tuning
=================================================
Evaluates RAG performance across 2 configurations on 15-question eval set.

Configurations:
- Config A (chunk_500_topk_3): chunk_size=500, overlap=80, top_k=3
- Config B (chunk_300_topk_5): chunk_size=300, overlap=50, top_k=5

Metrics:
- Retrieval Hit Rate: Expected page appears in retrieved chunks
- Answer Keyword Recall: Percentage of expected keywords in answer
- Q6 Abstention Pass: Correctly says "I don't know" for Q6
- Citation Rate: Percentage with non-empty citations
- Average Latency: Response time in milliseconds

Output:
- Console table comparing Config A vs Config B
- Detailed report saved to eval/rag_eval_results.md

Run with:
    python -m eval.run_eval
"""

import json
import os
import sys
import time
from typing import Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.rag import answer_question


def load_eval_set(path: str = "eval/eval_set.json") -> list[dict[str, Any]]:
    """Load evaluation set from JSON."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def compute_keyword_recall(answer: str, expected_keywords: list[str]) -> float:
    """Compute percentage of expected keywords present in answer."""
    if not expected_keywords:
        return 1.0

    answer_lower = answer.lower()
    matches = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
    return matches / len(expected_keywords)


def check_retrieval_hit(citations: list[dict], expected_page: int) -> bool:
    """Check if expected page appears in retrieved citations."""
    if expected_page is None:
        return True  # N/A for unanswerable questions

    for citation in citations:
        if citation.get("page") == expected_page:
            return True

    return False


def evaluate_config(
    eval_set: list[dict[str, Any]],
    config_name: str,
    chunk_size: int,
    overlap: int,
    top_k: int
) -> dict[str, Any]:
    """
    Evaluate RAG performance on eval set with given configuration.

    Returns:
        Dictionary with metrics and detailed results
    """
    print(f"\n{'=' * 70}")
    print(f"Evaluating {config_name}")
    print(f"  chunk_size={chunk_size}, overlap={overlap}, top_k={top_k}")
    print(f"{'=' * 70}\n")

    results = []
    total_latency = 0
    retrieval_hits = 0
    total_keyword_recall = 0.0
    q6_abstention_pass = False
    citations_present = 0
    answerable_count = 0

    for item in eval_set:
        q_id = item["id"]
        question = item["question"]
        expected_keywords = item["expected_keywords"]
        expected_page = item["expected_source_page"]
        answerable = item["answerable"]

        print(f"Q{q_id}: {question[:60]}...")

        # Call RAG
        start_time = time.time()
        try:
            response = answer_question(
                question,
                top_k=top_k,
                chunk_size=chunk_size,
                overlap=overlap
            )
            latency_ms = (time.time() - start_time) * 1000
        except Exception as e:
            print(f"  ERROR: {e}")
            response = {
                "question": question,
                "answer": "ERROR",
                "citations": [],
                "confidence": "low",
                "abstained": False
            }
            latency_ms = 0

        total_latency += latency_ms

        # Compute metrics
        answer = response.get("answer", "")
        citations = response.get("citations", [])
        abstained = response.get("abstained", False)

        # Retrieval hit rate
        if answerable:
            hit = check_retrieval_hit(citations, expected_page)
            if hit:
                retrieval_hits += 1
            print(f"  Retrieval Hit: {'PASS' if hit else 'FAIL'}")

        # Keyword recall
        recall = compute_keyword_recall(answer, expected_keywords)
        total_keyword_recall += recall
        print(f"  Keyword Recall: {recall:.1%}")

        # Q6 abstention check
        if q_id == 6:
            q6_correct = ("don't know" in answer.lower() or "do not know" in answer.lower())
            q6_abstention_pass = q6_correct
            print(f"  Q6 Abstention: {'PASS' if q6_correct else 'FAIL'}")

        # Citation presence
        if answerable and len(citations) > 0:
            citations_present += 1

        if answerable:
            answerable_count += 1

        # Store result
        results.append({
            "id": q_id,
            "question": question,
            "answer": answer,
            "citations": citations,
            "confidence": response.get("confidence", "low"),
            "abstained": abstained,
            "latency_ms": latency_ms,
            "keyword_recall": recall,
            "retrieval_hit": check_retrieval_hit(citations, expected_page) if answerable else None,
        })

        print(f"  Latency: {latency_ms:.0f} ms")
        print()

    # Compute aggregate metrics
    retrieval_hit_rate = retrieval_hits / answerable_count if answerable_count > 0 else 0
    avg_keyword_recall = total_keyword_recall / len(eval_set)
    citation_rate = citations_present / answerable_count if answerable_count > 0 else 0
    avg_latency = total_latency / len(eval_set)

    return {
        "config_name": config_name,
        "chunk_size": chunk_size,
        "overlap": overlap,
        "top_k": top_k,
        "results": results,
        "metrics": {
            "retrieval_hit_rate": retrieval_hit_rate,
            "avg_keyword_recall": avg_keyword_recall,
            "q6_abstention_pass": q6_abstention_pass,
            "citation_rate": citation_rate,
            "avg_latency_ms": avg_latency,
        }
    }


def print_comparison_table(config_a: dict, config_b: dict):
    """Print side-by-side comparison table."""
    print("\n" + "=" * 70)
    print("RAG EVALUATION RESULTS — Configuration Comparison")
    print("=" * 70)
    print()

    metrics_a = config_a["metrics"]
    metrics_b = config_b["metrics"]

    print(f"{'Metric':<35} {'Config A':<17} {'Config B':<17}")
    print("-" * 70)
    print(f"{'Configuration':<35} {'chunk_500_topk_3':<17} {'chunk_300_topk_5':<17}")
    print(f"{'Chunk Size':<35} {config_a['chunk_size']:<17} {config_b['chunk_size']:<17}")
    print(f"{'Overlap':<35} {config_a['overlap']:<17} {config_b['overlap']:<17}")
    print(f"{'Top-K':<35} {config_a['top_k']:<17} {config_b['top_k']:<17}")
    print("-" * 70)
    print(f"{'Retrieval Hit Rate (%)':<35} {metrics_a['retrieval_hit_rate']*100:<17.1f} {metrics_b['retrieval_hit_rate']*100:<17.1f}")
    print(f"{'Avg Keyword Recall (%)':<35} {metrics_a['avg_keyword_recall']*100:<17.1f} {metrics_b['avg_keyword_recall']*100:<17.1f}")
    print(f"{'Q6 Abstention Pass':<35} {'PASS' if metrics_a['q6_abstention_pass'] else 'FAIL':<17} {'PASS' if metrics_b['q6_abstention_pass'] else 'FAIL':<17}")
    print(f"{'Citation Rate (%)':<35} {metrics_a['citation_rate']*100:<17.1f} {metrics_b['citation_rate']*100:<17.1f}")
    print(f"{'Avg Latency (ms)':<35} {metrics_a['avg_latency_ms']:<17.0f} {metrics_b['avg_latency_ms']:<17.0f}")
    print("=" * 70)

    # Determine winner
    score_a = (
        metrics_a['retrieval_hit_rate'] * 0.3 +
        metrics_a['avg_keyword_recall'] * 0.3 +
        (1.0 if metrics_a['q6_abstention_pass'] else 0.0) * 0.2 +
        metrics_a['citation_rate'] * 0.2
    )

    score_b = (
        metrics_b['retrieval_hit_rate'] * 0.3 +
        metrics_b['avg_keyword_recall'] * 0.3 +
        (1.0 if metrics_b['q6_abstention_pass'] else 0.0) * 0.2 +
        metrics_b['citation_rate'] * 0.2
    )

    if score_a > score_b:
        winner = "Config A (chunk_500_topk_3)"
    elif score_b > score_a:
        winner = "Config B (chunk_300_topk_5)"
    else:
        winner = "TIE"

    print(f"\nWINNER: {winner}")
    print(f"   Config A Score: {score_a:.3f}")
    print(f"   Config B Score: {score_b:.3f}")
    print()

    return winner, score_a, score_b


def save_detailed_report(config_a: dict, config_b: dict, winner: str, output_path: str = "eval/rag_eval_results.md"):
    """Save detailed evaluation report to markdown."""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# RAG Evaluation Results — Day 8\n\n")
        f.write("**Student:** Abhishek Sanjay Dighe (2124UMLM2056)  \n")
        f.write("**Project:** SJ-64 SuryaGharSathi  \n")
        f.write("**Date:** Day 8 — RAG Pipeline & Evaluation  \n\n")
        f.write("---\n\n")

        f.write("## Overview\n\n")
        f.write("This report evaluates RAG (Retrieval-Augmented Generation) performance across 2 chunk/retrieval configurations ")
        f.write("on a 15-question evaluation set covering PM Surya Ghar: Muft Bijli Yojana guidelines.\n\n")

        f.write("**Evaluation Set:** 15 questions (10 from Day 5 + 5 additional guideline questions)  \n")
        f.write("**Configurations Tested:** 2  \n")
        f.write("**Metrics:** Retrieval Hit Rate, Keyword Recall, Q6 Abstention, Citation Rate, Latency  \n\n")

        f.write("---\n\n")

        # Configuration comparison table
        f.write("## Configuration Comparison\n\n")
        f.write("| Metric | Config A (chunk_500_topk_3) | Config B (chunk_300_topk_5) |\n")
        f.write("|--------|----------------------------|----------------------------|\n")
        f.write(f"| **Chunk Size** | {config_a['chunk_size']} | {config_b['chunk_size']} |\n")
        f.write(f"| **Overlap** | {config_a['overlap']} | {config_b['overlap']} |\n")
        f.write(f"| **Top-K** | {config_a['top_k']} | {config_b['top_k']} |\n")
        f.write(f"| **Retrieval Hit Rate** | {config_a['metrics']['retrieval_hit_rate']*100:.1f}% | {config_b['metrics']['retrieval_hit_rate']*100:.1f}% |\n")
        f.write(f"| **Avg Keyword Recall** | {config_a['metrics']['avg_keyword_recall']*100:.1f}% | {config_b['metrics']['avg_keyword_recall']*100:.1f}% |\n")
        f.write(f"| **Q6 Abstention Pass** | {'✓ PASS' if config_a['metrics']['q6_abstention_pass'] else '✗ FAIL'} | {'✓ PASS' if config_b['metrics']['q6_abstention_pass'] else '✗ FAIL'} |\n")
        f.write(f"| **Citation Rate** | {config_a['metrics']['citation_rate']*100:.1f}% | {config_b['metrics']['citation_rate']*100:.1f}% |\n")
        f.write(f"| **Avg Latency (ms)** | {config_a['metrics']['avg_latency_ms']:.0f} | {config_b['metrics']['avg_latency_ms']:.0f} |\n\n")

        f.write(f"### 🏆 Winner: {winner}\n\n")

        f.write("---\n\n")

        # Detailed results for Config A
        f.write("## Detailed Results — Config A (chunk_500_topk_3)\n\n")
        for result in config_a['results']:
            f.write(f"### Q{result['id']}\n\n")
            f.write(f"**Question:** {result['question']}\n\n")
            f.write(f"**Answer:** {result['answer'][:300]}...\n\n")
            f.write(f"**Keyword Recall:** {result['keyword_recall']:.1%}  \n")
            f.write(f"**Retrieval Hit:** {'✓' if result.get('retrieval_hit') else ('✗' if result.get('retrieval_hit') is not None else 'N/A')}  \n")
            f.write(f"**Citations:** {len(result['citations'])}  \n")
            f.write(f"**Latency:** {result['latency_ms']:.0f} ms  \n\n")

            if result['citations']:
                f.write("**Citation Details:**\n")
                f.writelines(f"{i}. {cite['chunk_id']} (Page {cite['page']}, Score: {cite['score']:.3f})\n" for i, cite in enumerate(result['citations'][:3], 1))
                f.write("\n")

            f.write("---\n\n")

        # Detailed results for Config B
        f.write("## Detailed Results — Config B (chunk_300_topk_5)\n\n")
        for result in config_b['results']:
            f.write(f"### Q{result['id']}\n\n")
            f.write(f"**Question:** {result['question']}\n\n")
            f.write(f"**Answer:** {result['answer'][:300]}...\n\n")
            f.write(f"**Keyword Recall:** {result['keyword_recall']:.1%}  \n")
            f.write(f"**Retrieval Hit:** {'✓' if result.get('retrieval_hit') else ('✗' if result.get('retrieval_hit') is not None else 'N/A')}  \n")
            f.write(f"**Citations:** {len(result['citations'])}  \n")
            f.write(f"**Latency:** {result['latency_ms']:.0f} ms  \n\n")

            if result['citations']:
                f.write("**Citation Details:**\n")
                f.writelines(f"{i}. {cite['chunk_id']} (Page {cite['page']}, Score: {cite['score']:.3f})\n" for i, cite in enumerate(result['citations'][:3], 1))
                f.write("\n")

            f.write("---\n\n")

        f.write("## Conclusion\n\n")
        f.write(f"The evaluation shows that **{winner}** performs better overall on the 15-question ")
        f.write("benchmark, balancing retrieval accuracy, answer quality, and citation completeness.\n\n")

        f.write("**Key Insights:**\n\n")
        f.write("- **Retrieval Hit Rate:** Measures whether the expected source page appears in retrieved chunks\n")
        f.write("- **Keyword Recall:** Percentage of expected keywords present in the generated answer\n")
        f.write("- **Q6 Abstention:** Critical test for handling unanswerable/out-of-scope questions\n")
        f.write("- **Citation Rate:** Ensures grounded answers with proper source attribution\n\n")

        f.write("---\n\n")
        f.write("**Report Generated:** Day 8  \n")
        f.write("**Status:** Complete ✓\n")

    print(f"Detailed report saved to {output_path}")


def main():
    """Run RAG evaluation on both configurations."""

    print("=" * 70)
    print("SuryaGharSathi RAG Evaluation Runner")
    print("Student: Abhishek Sanjay Dighe (2124UMLM2056)")
    print("Project: SJ-64 SuryaGharSathi")
    print("=" * 70)

    # Load evaluation set
    eval_set = load_eval_set()
    print(f"\nLoaded {len(eval_set)} evaluation questions")

    # Evaluate Config A
    config_a = evaluate_config(
        eval_set,
        config_name="Config A (chunk_500_topk_3)",
        chunk_size=500,
        overlap=80,
        top_k=3
    )

    # Evaluate Config B
    config_b = evaluate_config(
        eval_set,
        config_name="Config B (chunk_300_topk_5)",
        chunk_size=300,
        overlap=50,
        top_k=5
    )

    # Print comparison
    winner, _score_a, _score_b = print_comparison_table(config_a, config_b)

    # Save detailed report
    save_detailed_report(config_a, config_b, winner)

    print("\n" + "=" * 70)
    print("Evaluation complete!")
    print("See eval/rag_eval_results.md for detailed results")
    print("=" * 70)


if __name__ == "__main__":
    main()
