"""
LLM CLASSIFIER FOR CONVERSATIONAL COMMERCE INTELLIGENCE
LEVEL 3: Ollama/LLaMA Integration

This module replaces the stub classifier with a real LLM.
Classification uses the locked prompt from llm_prompt.py.

LLM suggests → System validates → Business logic corrects.
"""

import json
import ollama
from typing import Dict, Any
from llm_prompt import build_classification_prompt


class LLMClassifier:
    """
    LLM-based classifier using Ollama API.
    
    Locked Settings (DO NOT CHANGE):
    - temperature: 0.1 (low creativity, high consistency)
    - top_p: 0.9 (high determinism)
    - num_predict: 200 (max tokens for response)
    """
    
    def __init__(
        self, 
        model: str = "llama3.1:latest",
        api_url: str = "http://localhost:11434"
    ):
        """
        Initialize LLM classifier.
        
        Args:
            model: Ollama model name (default: llama3.1:latest)
            api_url: Ollama API endpoint (default: localhost:11434)
        """
        self.model = model
        self.api_url = api_url
        
        # Locked generation settings
        self.temperature = 0.1
        self.top_p = 0.9
        self.num_predict = 200
        
    def classify(self, user_message: str, assistant_reply: str = "") -> Dict[str, Any]:
        """
        Classify shopper message using LLM.
        
        Pipeline:
        1. Build prompt (system + user input)
        2. Call Ollama API
        3. Parse JSON response
        4. Return output dict
        
        Args:
            user_message: Shopper's message
            assistant_reply: Assistant's response (optional)
            
        Returns:
            Dictionary with intent, objection, purchase_stage, sentiment, confidence
            
        Raises:
            ValueError: If LLM returns invalid JSON or missing fields
            Exception: If Ollama API call fails
        """
        if not user_message or not user_message.strip():
            raise ValueError("user_message cannot be empty")
        
        # Step 1: Build the prompt using locked template
        prompt = build_classification_prompt(user_message, assistant_reply)
        
        # Step 2: Call Ollama API with locked settings
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': self.temperature,
                    'top_p': self.top_p,
                    'num_predict': self.num_predict
                },
                stream=False
            )
        except Exception as e:
            raise Exception(f"Ollama API call failed: {e}")
        
        # Step 3: Parse JSON response
        try:
            raw_response = response['response'].strip()
            
            # Sometimes LLMs wrap JSON in markdown code blocks
            if raw_response.startswith("```json"):
                raw_response = raw_response.replace("```json", "").replace("```", "").strip()
            elif raw_response.startswith("```"):
                raw_response = raw_response.replace("```", "").strip()
            
            output = json.loads(raw_response)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM returned invalid JSON: {e}\nResponse: {response['response']}")
        
        # Step 4: Basic validation (required fields present)
        required_fields = ['intent', 'objection', 'purchase_stage', 'sentiment', 'confidence']
        missing_fields = [field for field in required_fields if field not in output]
        
        if missing_fields:
            raise ValueError(f"LLM output missing fields: {missing_fields}")
        
        return output


# Test function for quick validation
def test_llm_classifier():
    """Quick test to verify LLM classifier works."""
    classifier = LLMClassifier()
    
    test_cases = [
        {
            "user_message": "I want to buy the Premium Waterproof Hoodie in size L.",
            "assistant_reply": "Great choice! I'll add it to your cart."
        },
        {
            "user_message": "I'm worried it won't fit me. I'm 6 feet tall.",
            "assistant_reply": "It has an oversized fit and we offer free returns."
        },
        {
            "user_message": "How much is this?",
            "assistant_reply": "The Premium Waterproof Hoodie is ₹6,999."
        }
    ]
    
    print("=" * 60)
    print("LLM CLASSIFIER TEST")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[Test {i}]")
        print(f"User: {test['user_message']}")
        print(f"Assistant: {test['assistant_reply']}")
        
        try:
            result = classifier.classify(
                test['user_message'],
                test['assistant_reply']
            )
            print(f"\nResult:")
            print(f"  Intent: {result['intent']}")
            print(f"  Objection: {result['objection']}")
            print(f"  Stage: {result['purchase_stage']}")
            print(f"  Sentiment: {result['sentiment']}")
            print(f"  Confidence: {result['confidence']}")
            print(f"[OK]")
        except Exception as e:
            print(f"[FAILED] {e}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_llm_classifier()
