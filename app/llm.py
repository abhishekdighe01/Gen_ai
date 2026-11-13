"""
Day 6 — Enhanced LLM Module
============================
Multi-provider LLM wrapper supporting Groq and Google Gemini with:
- Prompt template management
- Structured JSON output parsing
- Offline fallback using RAG
- Environment-based configuration

Supports:
- Groq (Llama 3.3 70B, Llama 3.1 8B)
- Google Gemini (Gemini 2.0 Flash, Gemini 1.5 Flash)
- Offline/fallback mode with smart_search
"""

import os
import json
import re
from typing import Dict, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import API clients
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Import RAG components for fallback
try:
    from app.smart_search import smart_search
    from app.records import load_records
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False


class PromptManager:
    """Manages loading and formatting of prompt templates."""
    
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(prompts_dir)
        self._cache = {}
    
    def load_prompt(self, filename: str) -> str:
        """Load a prompt template from file."""
        if filename in self._cache:
            return self._cache[filename]
        
        filepath = self.prompts_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Prompt file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self._cache[filename] = content
        return content
    
    def format_prompt(self, template: str, **kwargs) -> str:
        """Format a prompt template with variables."""
        return template.format(**kwargs)


class LLMClient:
    """
    Multi-provider LLM client with structured output.
    
    Supports:
    - Groq (llama-3.3-70b-versatile, llama-3.1-8b-instant)
    - Google Gemini (gemini-2.0-flash-exp, gemini-1.5-flash)
    - Offline fallback with RAG
    """
    
    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1500,
    ):
        # Load configuration from environment
        self.provider = provider or os.getenv("LLM_PROVIDER", "groq")
        self.model = model or os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize prompt manager
        self.prompt_manager = PromptManager()
        
        # Get API key
        if api_key is None:
            if self.provider == "groq":
                api_key = os.getenv("GROQ_API_KEY")
            elif self.provider == "gemini":
                api_key = os.getenv("GEMINI_API_KEY")
        
        self.api_key = api_key
        self.client = None
        
        # Initialize provider client if API key available
        if self.api_key and self.api_key not in ["your_groq_api_key_here", "your_gemini_api_key_here", "gsk_demo_key_for_testing"]:
            if self.provider == "groq" and GROQ_AVAILABLE:
                self.client = Groq(api_key=self.api_key)
            elif self.provider == "gemini" and GEMINI_AVAILABLE:
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model)
    
    def _call_groq(self, messages: list) -> str:
        """Call Groq API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content.strip()
    
    def _call_gemini(self, prompt: str) -> str:
        """Call Google Gemini API."""
        response = self.client.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            )
        )
        return response.text.strip()
    
    def _fallback_response(self, question: str, context: str = "") -> Dict[str, str]:
        """
        Offline fallback using RAG search.
        Returns structured response without calling LLM API.
        """
        if not RAG_AVAILABLE:
            return {
                "answer": "LLM is not configured and RAG components are unavailable. Please set GROQ_API_KEY or GEMINI_API_KEY in .env file.",
                "confidence": "low",
                "follow_up": "Would you like help getting started with API configuration?"
            }
        
        # Search for relevant records
        try:
            results = smart_search(question, top_k=3)
            
            if not results:
                return {
                    "answer": "I don't know - this question is outside the scope of PM Surya Ghar: Muft Bijli Yojana guidelines. No relevant information found in the dataset.",
                    "confidence": "high",
                    "follow_up": "Would you like to ask about CFA subsidy rates, eligibility criteria, or the installation process?"
                }
            
            # Build answer from top result
            top_record, score = results[0]
            
            if score < 0.15:  # Low relevance threshold
                return {
                    "answer": "I don't know - this question is outside the scope of PM Surya Ghar guidelines. The available information does not adequately address your question.",
                    "confidence": "high",
                    "follow_up": "Please ask about residential rooftop solar subsidies, eligibility, or installation procedures."
                }
            
            # Construct answer from retrieved record
            answer = f"{top_record.key_rule}\n\nSource: {top_record.source_section}"
            
            # Determine confidence based on relevance score
            if score > 0.4:
                confidence = "high"
            elif score > 0.25:
                confidence = "medium"
            else:
                confidence = "low"
            
            # Generate follow-up based on topic
            follow_ups = {
                "CFA": "How do I calculate the exact subsidy for my system size?",
                "eligibility": "What documents do I need to apply?",
                "DISCOM": "How long does MSEDCL approval typically take?",
                "DCR": "How can I verify if solar panels are DCR-compliant?",
            }
            
            follow_up = "Would you like more details about the installation process or DISCOM procedures?"
            for keyword, fq in follow_ups.items():
                if keyword.lower() in top_record.topic.lower():
                    follow_up = fq
                    break
            
            return {
                "answer": answer,
                "confidence": confidence,
                "follow_up": follow_up
            }
        
        except Exception as e:
            return {
                "answer": f"Error generating response: {str(e)}",
                "confidence": "low",
                "follow_up": "Please try rephrasing your question."
            }
    
    def _parse_json_response(self, text: str) -> Optional[Dict]:
        """
        Extract and parse JSON from LLM response.
        Handles cases where LLM adds extra text before/after JSON.
        """
        # Try to find JSON block
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if not json_match:
            return None
        
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            return None
    
    def generate(
        self,
        question: str,
        context: str = "",
        prompt_version: str = "v2"
    ) -> Dict[str, str]:
        """
        Generate structured response with answer, confidence, and follow_up.
        
        Args:
            question: User's question
            context: Retrieved context from RAG (optional)
            prompt_version: "v1" or "v2" for prompt template selection
        
        Returns:
            Dict with keys: answer, confidence, follow_up
        """
        # If no API key, use fallback
        if not self.client:
            return self._fallback_response(question, context)
        
        try:
            # Load prompts
            system_prompt = self.prompt_manager.load_prompt("system_prompt.txt")
            
            if prompt_version == "v1":
                task_prompt_template = self.prompt_manager.load_prompt("task_v1_basic.txt")
                task_prompt = self.prompt_manager.format_prompt(
                    task_prompt_template,
                    question=question
                )
            else:  # v2
                task_prompt_template = self.prompt_manager.load_prompt("task_v2_structured.txt")
                task_prompt = self.prompt_manager.format_prompt(
                    task_prompt_template,
                    question=question,
                    context=context if context else "No additional context provided."
                )
            
            # Call appropriate API
            if self.provider == "groq":
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": task_prompt}
                ]
                response_text = self._call_groq(messages)
            
            elif self.provider == "gemini":
                # Gemini doesn't support separate system messages, combine them
                combined_prompt = f"{system_prompt}\n\n{task_prompt}"
                response_text = self._call_gemini(combined_prompt)
            
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
            
            # Parse JSON response
            parsed = self._parse_json_response(response_text)
            
            if parsed and all(k in parsed for k in ["answer", "confidence", "follow_up"]):
                return parsed
            else:
                # If parsing failed, construct response
                return {
                    "answer": response_text,
                    "confidence": "medium",
                    "follow_up": "Would you like more information about this topic?"
                }
        
        except Exception as e:
            # On any error, use fallback
            print(f"LLM API error: {e}")
            return self._fallback_response(question, context)


# Global instance
_llm_client = None


def get_llm_client() -> LLMClient:
    """Get or create singleton LLM client."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


def generate_chat_response(
    question: str,
    prompt_version: str = "v2",
    use_rag: bool = True,
    top_k: int = 5
) -> Dict[str, str]:
    """
    Main entry point for generating chat responses.
    
    Args:
        question: User question
        prompt_version: "v1" or "v2"
        use_rag: Whether to retrieve context
        top_k: Number of records to retrieve
    
    Returns:
        Dict with answer, confidence, follow_up
    """
    client = get_llm_client()
    
    # Retrieve context if RAG enabled
    context = ""
    if use_rag and RAG_AVAILABLE:
        try:
            results = smart_search(question, top_k=top_k)
            if results:
                context_parts = []
                for record, score in results:
                    context_parts.append(
                        f"[Relevance: {score:.3f}]\n"
                        f"Topic: {record.topic}\n"
                        f"Rule: {record.key_rule}\n"
                        f"Source: {record.source_section}"
                    )
                context = "\n\n".join(context_parts)
        except Exception as e:
            print(f"RAG retrieval error: {e}")
    
    return client.generate(question, context, prompt_version)


if __name__ == "__main__":
    """Test the LLM client with sample questions."""
    
    print("=" * 70)
    print("SuryaGharSathi LLM Client Test (Day 6)")
    print("=" * 70)
    print()
    
    # Test configuration
    provider = os.getenv("LLM_PROVIDER", "groq")
    model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    api_key = os.getenv("GROQ_API_KEY") if provider == "groq" else os.getenv("GEMINI_API_KEY")
    
    print("Configuration:")
    print(f"  Provider: {provider}")
    print(f"  Model: {model}")
    print(f"  API Key: {'Configured' if api_key and api_key not in ['your_groq_api_key_here', 'your_gemini_api_key_here'] else 'NOT configured (using fallback)'}")
    print()
    
    # Test questions
    test_questions = [
        ("How much subsidy for 2.5 kW?", "v2"),
        ("What will MSEDCL tariff be next year?", "v2"),  # Out-of-scope
        ("Are imported panels eligible?", "v1"),
    ]
    
    for i, (question, version) in enumerate(test_questions, 1):
        print(f"Test {i}: {question}")
        print(f"  Prompt version: {version}")
        
        response = generate_chat_response(question, prompt_version=version, use_rag=True)
        
        print(f"  Answer: {response['answer'][:100]}...")
        print(f"  Confidence: {response['confidence']}")
        print(f"  Follow-up: {response['follow_up']}")
        print()
    
    print("=" * 70)
    print("Test complete!")
    print("=" * 70)
