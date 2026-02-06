"""
Stub Classifier Implementation
LEVEL 2 STEP D.2 - Stub-Based Classification

This is a TEMPORARY classifier that uses keyword matching
to return valid schema outputs.

PURPOSE:
- Test schema validation
- Test business logic enforcement
- Isolate system logic from model behavior
- DO NOT call Ollama yet

CRITICAL: This must be replaced with LLM classifier in Level 3.
This is for testing ONLY.
"""

import re
from typing import Dict
from schema import (
    IntelligenceOutput,
    Intent,
    Objection,
    PurchaseStage,
    Sentiment
)


class StubClassifier:
    """
    Keyword-based stub classifier for testing.
    
    Uses simple pattern matching to classify messages.
    Returns valid IntelligenceOutput schema objects.
    """
    
    def classify(self, user_message: str, assistant_reply: str = "") -> IntelligenceOutput:
        """
        Classify a shopper message using keyword matching.
        
        Args:
            user_message: The shopper's message
            assistant_reply: The assistant's response (affects sentiment)
            
        Returns:
            Valid IntelligenceOutput object
        """
        
        # Normalize for matching
        msg_lower = user_message.lower()
        
        # Classify intent (most specific first)
        intent = self._classify_intent(msg_lower)
        
        # Classify objection
        objection = self._classify_objection(msg_lower)
        
        # Infer purchase stage from intent (will be corrected by business logic)
        purchase_stage = self._infer_stage(intent, objection)
        
        # Classify sentiment
        sentiment = self._classify_sentiment(msg_lower, assistant_reply)
        
        # Stub confidence (keyword-based = medium confidence)
        confidence = self._estimate_confidence(msg_lower)
        
        return {
            "intent": intent,
            "objection": objection,
            "purchase_stage": purchase_stage,
            "sentiment": sentiment,
            "confidence": confidence
        }
    
    def _classify_intent(self, msg: str) -> str:
        """Classify intent using keyword patterns."""
        
        # Price evaluation
        if any(word in msg for word in ["expensive", "price", "cost", "worth", "cheap"]):
            return Intent.PRICE_EVALUATION.value
        
        # Fit validation
        if any(word in msg for word in ["size", "fit", "fits", "fitting", "loose", "tight", "oversized", "slim"]):
            return Intent.FIT_VALIDATION.value
        
        # Product comparison
        if any(word in msg for word in ["compare", "difference", "versus", "vs", "better", "which one"]):
            return Intent.PRODUCT_COMPARISON.value
        
        # Purchase readiness
        if any(word in msg for word in ["buy", "purchase", "order", "checkout", "ready"]):
            return Intent.PURCHASE_READINESS.value
        
        # Policy clarification
        if any(word in msg for word in ["return", "refund", "shipping", "delivery", "exchange", "policy"]):
            return Intent.POLICY_CLARIFICATION.value
        
        # Browsing (default for exploratory queries)
        if any(word in msg for word in ["show", "looking", "browse", "what", "available", "options"]):
            return Intent.BROWSING.value
        
        # Fallback
        return Intent.BROWSING.value
    
    def _classify_objection(self, msg: str) -> str:
        """Classify objection using keyword patterns."""
        
        # Price sensitivity
        if any(word in msg for word in ["expensive", "too much", "budget", "cheaper", "afford"]):
            return Objection.PRICE_SENSITIVITY.value
        
        # Fit uncertainty
        if any(word in msg for word in ["not sure", "uncertain", "will it fit", "worried about", "concern"]) \
           and any(word in msg for word in ["size", "fit"]):
            return Objection.FIT_UNCERTAINTY.value
        
        # Trust/quality concern
        if any(word in msg for word in ["quality", "trust", "reliable", "genuine", "fake", "worth it"]):
            return Objection.TRUST_QUALITY_CONCERN.value
        
        # Delivery/returns risk
        if any(word in msg for word in ["return", "refund", "shipping", "delivery time"]):
            return Objection.DELIVERY_RETURNS_RISK.value
        
        # Choice overload
        if any(word in msg for word in ["too many", "confused", "overwhelmed", "which one", "can't decide"]):
            return Objection.CHOICE_OVERLOAD.value
        
        # No objection detected
        return Objection.NONE.value
    
    def _infer_stage(self, intent: str, objection: str) -> str:
        """
        Infer purchase stage based on intent.
        
        Note: This will be corrected by business logic if wrong.
        """
        
        # Early stage intents
        if intent in [Intent.BROWSING.value]:
            return PurchaseStage.EARLY.value
        
        # Decision stage intents
        if intent in [Intent.PRICE_EVALUATION.value, Intent.PURCHASE_READINESS.value]:
            return PurchaseStage.DECISION.value
        
        # Default to consideration
        return PurchaseStage.CONSIDERATION.value
    
    def _classify_sentiment(self, msg: str, assistant_reply: str) -> str:
        """Classify sentiment using keyword patterns."""
        
        # Anxious signals
        if any(word in msg for word in ["worried", "nervous", "unsure", "not sure", "concerned", "afraid"]):
            # If assistant provided reassurance, downgrade to neutral
            if assistant_reply and any(word in assistant_reply.lower() for word in ["free returns", "guarantee", "risk-free"]):
                return Sentiment.NEUTRAL.value
            return Sentiment.ANXIOUS.value
        
        # Hesitant signals
        if any(word in msg for word in ["but", "however", "though", "expensive", "hmm", "maybe"]):
            return Sentiment.HESITANT.value
        
        # Positive signals
        if any(word in msg for word in ["great", "good", "nice", "love", "perfect", "excellent"]):
            return Sentiment.POSITIVE.value
        
        # Default neutral
        return Sentiment.NEUTRAL.value
    
    def _estimate_confidence(self, msg: str) -> float:
        """
        Estimate confidence based on message clarity.
        
        Stub logic: keyword-based = medium confidence
        """
        
        # Very short messages = lower confidence
        if len(msg.split()) < 3:
            return 0.6
        
        # Question marks = slightly higher confidence (clear intent)
        if "?" in msg:
            return 0.75
        
        # Default stub confidence
        return 0.7
