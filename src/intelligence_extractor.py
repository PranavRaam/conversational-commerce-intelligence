"""
Intelligence Extractor - The Core Level 2 Function
LEVEL 2 STEP D.5 - Main Extractor with Retry Logic

This is THE function for Level 2.
Everything else exists to support this.

PUBLIC API:
    extract_intelligence(user_message, assistant_reply)
    
Returns:
    Valid IntelligenceOutput OR fallback with confidence=0.0
"""

import json
from typing import Optional
from schema import IntelligenceOutput, get_fallback_output
from validator import validate_schema, ValidationError
from business_logic import enforce_business_logic
from stub_classifier import StubClassifier
from llm_classifier import LLMClassifier


class IntelligenceExtractor:
    """
    Convert a single shopper message into structured intelligence.
    
    This is Level 2's public interface.
    
    Flow:
    1. Classify (using stub for now)
    2. Validate schema
    3. Apply business logic
    4. Retry once if validation fails
    5. Return fallback if still fails
    """
    
    def __init__(self, use_stub: bool = True, llm_model: str = "llama3.1:latest"):
        """
        Initialize the extractor.
        
        Args:
            use_stub: If True, use stub classifier. If False, use LLM (Level 3)
            llm_model: Ollama model name (only used if use_stub=False)
        """
        self.use_stub = use_stub
        self.llm_model = llm_model
        
        if use_stub:
            self.classifier = StubClassifier()
        else:
            self.classifier = LLMClassifier(model=llm_model)
        
        self.max_retries = 1
    
    def extract_intelligence(
        self,
        user_message: str,
        assistant_reply: str = ""
    ) -> IntelligenceOutput:
        """
        Extract structured intelligence from a shopper message.
        
        This is the ONLY public function for Level 2.
        
        Args:
            user_message: The shopper's message
            assistant_reply: The assistant's response (optional)
            
        Returns:
            IntelligenceOutput: Validated, business-logic-corrected output
            OR fallback output if classification fails after retry
        """
        
        # Validate inputs
        if not user_message or not user_message.strip():
            return get_fallback_output()
        
        # Try classification with retry
        for attempt in range(self.max_retries + 1):
            try:
                # Step 1: Classify
                raw_output = self._classify(user_message, assistant_reply)
                
                # Step 2: Validate schema
                is_valid, error = validate_schema(raw_output)
                if not is_valid:
                    raise ValidationError(error)
                
                # Step 3: Apply business logic (with user message for keyword-based rules)
                corrected_output = enforce_business_logic(raw_output, user_message)
                
                # Step 4: Final validation (ensure business logic didn't break schema)
                is_valid, error = validate_schema(corrected_output)
                if not is_valid:
                    raise ValidationError(f"Business logic produced invalid output: {error}")
                
                return corrected_output
                
            except Exception as e:
                # Log the error (for now, just continue)
                if attempt < self.max_retries:
                    # Retry once
                    continue
                else:
                    # Max retries exceeded, return fallback
                    return get_fallback_output()
        
        # Should never reach here, but safety fallback
        return get_fallback_output()
    
    def _classify(self, user_message: str, assistant_reply: str) -> dict:
        """
        Classify the message using the configured classifier.
        
        Args:
            user_message: The shopper's message
            assistant_reply: The assistant's response
            
        Returns:
            Raw classification output (not yet validated)
        """
        # Both stub and LLM classifiers implement the same interface
        return self.classifier.classify(user_message, assistant_reply)


# Public API function (module-level convenience)
def extract_intelligence(
    user_message: str,
    assistant_reply: str = ""
) -> IntelligenceOutput:
    """
    Extract structured intelligence from a shopper message.
    
    This is Level 2's public API.
    
    Args:
        user_message: The shopper's message
        assistant_reply: The assistant's response (optional)
        
    Returns:
        IntelligenceOutput: Validated, corrected intelligence object
        
    Example:
        >>> result = extract_intelligence(
        ...     "Is this hoodie worth 5000?",
        ...     "Yes, it has premium fleece and reinforced stitching."
        ... )
        >>> print(result)
        {
            "intent": "price_evaluation",
            "objection": "price_sensitivity",
            "purchase_stage": "decision",
            "sentiment": "hesitant",
            "confidence": 0.75
        }
    """
    extractor = IntelligenceExtractor(use_stub=True)
    return extractor.extract_intelligence(user_message, assistant_reply)


if __name__ == "__main__":
    # Quick test examples
    print("Testing Intelligence Extractor\n" + "="*50)
    
    # Test 1: Price evaluation
    result1 = extract_intelligence("Is this hoodie worth 5000?")
    print("\nTest 1 - Price question:")
    print(json.dumps(result1, indent=2))
    
    # Test 2: Fit validation
    result2 = extract_intelligence("Will this fit me if I'm 6 feet tall?")
    print("\nTest 2 - Fit question:")
    print(json.dumps(result2, indent=2))
    
    # Test 3: Browsing
    result3 = extract_intelligence("Show me winter jackets")
    print("\nTest 3 - Browsing:")
    print(json.dumps(result3, indent=2))
    
    # Test 4: Invalid combo (browsing + price objection)
    result4 = extract_intelligence("What jackets do you have? They look expensive.")
    print("\nTest 4 - Invalid combo (should be corrected by business logic):")
    print(json.dumps(result4, indent=2))
    
    # Test 5: Empty input (should return fallback)
    result5 = extract_intelligence("")
    print("\nTest 5 - Empty input (fallback):")
    print(json.dumps(result5, indent=2))
    
    print("\n" + "="*50)
    print("✅ Level 2 Step D: COMPLETE")
