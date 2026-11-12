"""
Day 5 — LLM Integration
========================
Groq LLM client wrapper for SuryaGharSathi question answering.

Provides:
- LLM API client (Groq with Llama 3.1)
- System prompt for solar subsidy Q&A
- RAG context injection
- Error handling for API failures
"""

import os
from typing import Optional, List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Try to import Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Warning: groq package not installed. Run: pip install groq")


class LLMClient:
    """
    LLM client wrapper for question answering with RAG context.
    
    Supports:
    - Groq API (Llama 3.1, Mixtral)
    - System prompt injection
    - Context augmentation from retrieved records
    - Temperature and token controls
    """
    
    def __init__(
        self,
        provider: str = "groq",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1000,
    ):
        """
        Initialize LLM client.
        
        Args:
            provider: LLM provider ("groq" or "gemini")
            api_key: API key (reads from env if not provided)
            model: Model name (defaults from env)
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum response tokens
        """
        self.provider = provider.lower()
        
        # Load configuration from environment
        if api_key is None:
            if self.provider == "groq":
                api_key = os.getenv("GROQ_API_KEY")
            elif self.provider == "gemini":
                api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError(
                f"No API key found for provider '{self.provider}'. "
                f"Set {self.provider.upper()}_API_KEY in .env file."
            )
        
        self.api_key = api_key
        
        # Model selection
        if model is None:
            if self.provider == "groq":
                model = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
            elif self.provider == "gemini":
                model = os.getenv("GEMINI_MODEL", "gemini-pro")
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize client
        if self.provider == "groq":
            if not GROQ_AVAILABLE:
                raise ImportError(
                    "groq package is required. Install with: pip install groq"
                )
            self.client = Groq(api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[str] = None,
    ) -> str:
        """
        Generate LLM response for a user prompt.
        
        Args:
            prompt: User question/prompt
            system_prompt: System instructions for the LLM
            context: Retrieved context from RAG (optional)
        
        Returns:
            Generated response text
        
        Raises:
            Exception: If API call fails
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        # Build messages
        messages = []
        
        # Add system prompt
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Add context if provided
        if context:
            user_message = f"""Based on the following official guidelines:

{context}

Question: {prompt}

Answer based only on the guidelines provided above. If the information is not in the guidelines, say "I don't know - this is outside the scope of PM Surya Ghar guidelines."
"""
        else:
            user_message = prompt
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Call LLM API
        try:
            if self.provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                return response.choices[0].message.content.strip()
            else:
                raise ValueError(f"Provider {self.provider} not implemented")
        
        except Exception as e:
            raise Exception(f"LLM API call failed: {str(e)}")


def get_system_prompt() -> str:
    """
    Return the system prompt for SuryaGharSathi.
    
    This prompt instructs the LLM to:
    - Act as a PM Surya Ghar solar subsidy assistant
    - Answer based on official MNRE guidelines
    - Cite sources with section numbers
    - Refuse to speculate on out-of-scope questions
    - Provide accurate CFA calculations
    """
    return """You are SuryaGharSathi, an AI assistant helping homeowners understand the PM Surya Ghar: Muft Bijli Yojana rooftop solar subsidy scheme.

Your knowledge comes exclusively from official MNRE (Ministry of New and Renewable Energy) guidelines and notifications from 2024.

RULES:
1. Answer ONLY based on the provided guideline context - never speculate or use information outside the guidelines
2. For subsidy calculations, use the exact CFA rates from the guidelines:
   - General states: ₹30,000 per kW for first 2 kW, ₹18,000 per kW for additional capacity up to 3 kW
   - Special category states: ₹33,000 per kW for first 2 kW, ₹19,800 per kW for additional capacity up to 3 kW
   - NO CFA beyond 3 kW capacity
3. Always cite the source section (e.g., "per MNRE Guidelines Section 5(h)")
4. For questions outside the PM Surya Ghar scheme scope, respond: "I don't know - this is outside the scope of PM Surya Ghar guidelines."
5. Be helpful and clear, explaining technical terms when needed
6. Focus on residential rooftop solar eligibility and processes

EXAMPLE RESPONSES:
- Good: "For a 3 kW system, the CFA is ₹78,000 (₹60,000 for first 2 kW + ₹18,000 for 1 kW), per MNRE Guidelines Section 5(h)."
- Bad: "The subsidy is around ₹75,000-80,000" (too vague, no source)
- Good: "I don't know - electricity tariff rates are set by state regulatory commissions and are outside the PM Surya Ghar guidelines."

Your target user is a homeowner in Kopargaon, Maharashtra (MSEDCL area) with a ₹2,000/month electricity bill and 40 sq m terrace space."""


def build_rag_context(retrieved_records: List[Dict]) -> str:
    """
    Build RAG context string from retrieved records.
    
    Args:
        retrieved_records: List of record dicts with topic, key_rule, source_section
    
    Returns:
        Formatted context string for LLM prompt
    """
    if not retrieved_records:
        return ""
    
    context_parts = []
    for i, record in enumerate(retrieved_records, 1):
        topic = record.get("topic", "")
        rule = record.get("key_rule", "")
        section = record.get("source_section", "")
        
        context_parts.append(
            f"[{i}] Topic: {topic}\n"
            f"    Rule: {rule}\n"
            f"    Source: {section}"
        )
    
    return "\n\n".join(context_parts)


# Singleton instance for reuse
_llm_client_instance: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """
    Get or create singleton LLM client instance.
    
    Returns:
        Configured LLMClient instance
    
    Raises:
        ValueError: If API key is missing
        ImportError: If groq package not installed
    """
    global _llm_client_instance
    
    if _llm_client_instance is None:
        provider = os.getenv("LLM_PROVIDER", "groq")
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.3"))
        max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1000"))
        
        _llm_client_instance = LLMClient(
            provider=provider,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    
    return _llm_client_instance


if __name__ == "__main__":
    """Test the LLM client with a sample question."""
    
    print("=" * 70)
    print("SuryaGharSathi LLM Client Test")
    print("=" * 70)
    print()
    
    # Test 1: Check configuration
    print("1. Configuration Check")
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        print(f"   ✓ GROQ_API_KEY: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("   ✗ GROQ_API_KEY not found in environment")
    print()
    
    # Test 2: Initialize client
    print("2. Initialize LLM Client")
    try:
        client = get_llm_client()
        print(f"   ✓ Provider: {client.provider}")
        print(f"   ✓ Model: {client.model}")
        print(f"   ✓ Temperature: {client.temperature}")
    except Exception as e:
        print(f"   ✗ Failed to initialize: {e}")
        exit(1)
    print()
    
    # Test 3: Generate without context (simple test)
    print("3. Test Simple Generation (No RAG)")
    try:
        response = client.generate(
            prompt="What is PM Surya Ghar?",
            system_prompt=get_system_prompt(),
        )
        print(f"   Q: What is PM Surya Ghar?")
        print(f"   A: {response[:150]}...")
        print("   ✓ Generation successful")
    except Exception as e:
        print(f"   ✗ Generation failed: {e}")
    print()
    
    # Test 4: Generate with RAG context
    print("4. Test RAG-Enhanced Generation")
    mock_context = """[1] Topic: CFA Structure
    Rule: First 2 kW receives Rs 30000 per kW and additional 1 kW receives Rs 18000 per kW. No additional CFA beyond 3 kW.
    Source: MNRE Guidelines Section 5(e) and 5(h)

[2] Topic: CFA Example
    Rule: A 2.5 kW system receives Rs 69000 CFA under the standard category.
    Source: MNRE Guidelines Section 5(h)"""
    
    try:
        response = client.generate(
            prompt="How much subsidy for 2.5 kW?",
            system_prompt=get_system_prompt(),
            context=mock_context,
        )
        print(f"   Q: How much subsidy for 2.5 kW?")
        print(f"   A: {response}")
        print("   ✓ RAG generation successful")
    except Exception as e:
        print(f"   ✗ RAG generation failed: {e}")
    print()
    
    print("=" * 70)
    print("LLM Client Test Complete")
    print("=" * 70)
