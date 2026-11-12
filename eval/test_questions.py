"""
Day 5 — Question Evaluation Script
===================================
Test all 10 SuryaGharSathi questions against the /chat endpoint.

Requires:
- FastAPI server running on localhost:8000
- Valid GROQ_API_KEY in .env

Run with:
    python eval/test_questions.py
"""

import json
import requests
from typing import List, Dict

# API base URL
BASE_URL = "http://127.0.0.1:8000"


def load_questions() -> List[Dict]:
    """Load questions from questions.json."""
    with open("eval/questions.json", "r", encoding="utf-8") as f:
        return json.load(f)


def test_chat_endpoint(question: str, use_rag: bool = True) -> Dict:
    """
    Send a question to /chat endpoint.
    
    Args:
        question: User question
        use_rag: Whether to use RAG (default: True)
    
    Returns:
        Response dict with answer, sources, etc.
    """
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"question": question, "use_rag": use_rag, "top_k": 5},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"HTTP {response.status_code}",
                "detail": response.json().get("detail", "Unknown error")
            }
    
    except requests.exceptions.ConnectionError:
        return {
            "error": "Connection refused",
            "detail": "Is the FastAPI server running? Start with: uvicorn app.main:app --reload"
        }
    
    except Exception as e:
        return {
            "error": str(type(e).__name__),
            "detail": str(e)
        }


def evaluate_questions():
    """Run all 10 questions and display results."""
    
    print("=" * 80)
    print("SuryaGharSathi — Question Evaluation")
    print("=" * 80)
    print()
    
    # Load questions
    questions = load_questions()
    
    print(f"Loaded {len(questions)} questions from eval/questions.json")
    print()
    
    # Test each question
    results = []
    
    for q_data in questions:
        q_id = q_data["id"]
        question = q_data["question"]
        expected = q_data["expected_answer"]
        category = q_data["category"]
        out_of_scope = q_data.get("out_of_scope", False)
        
        print(f"Question {q_id}: {category}")
        print(f"  Q: {question[:70]}...")
        print(f"  Expected: {expected[:60]}...")
        
        # Call API
        response = test_chat_endpoint(question, use_rag=True)
        
        if "error" in response:
            print(f"  ✗ ERROR: {response['error']} - {response['detail']}")
            results.append({
                "id": q_id,
                "status": "error",
                "error": response["error"]
            })
        else:
            answer = response.get("answer", "")
            sources_count = response.get("rag_results_count", 0)
            
            print(f"  A: {answer[:100]}...")
            print(f"  RAG Sources: {sources_count}")
            
            # Check if out-of-scope is handled correctly
            if out_of_scope:
                contains_idk = "don't know" in answer.lower() or "outside" in answer.lower()
                status = "pass" if contains_idk else "fail"
                print(f"  Out-of-scope check: {'✓' if contains_idk else '✗'} {status}")
            else:
                status = "answered"
            
            results.append({
                "id": q_id,
                "status": status,
                "answer_length": len(answer),
                "sources_count": sources_count
            })
        
        print()
    
    # Summary
    print("=" * 80)
    print("Evaluation Summary")
    print("=" * 80)
    
    total = len(results)
    errors = sum(1 for r in results if r["status"] == "error")
    answered = sum(1 for r in results if r["status"] in ["answered", "pass"])
    out_of_scope_handled = sum(1 for r in results if r["status"] == "pass")
    
    print(f"Total questions: {total}")
    print(f"Answered: {answered}")
    print(f"Errors: {errors}")
    print(f"Out-of-scope handled correctly: {out_of_scope_handled}/1")
    
    if errors == 0:
        print()
        print("✓ All questions processed successfully!")
    else:
        print()
        print("✗ Some questions failed - check server logs")


if __name__ == "__main__":
    evaluate_questions()
