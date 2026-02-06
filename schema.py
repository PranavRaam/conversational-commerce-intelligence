"""
Schema Definition Module
LEVEL 2 STEP A - Output Schema Contract

This module defines the frozen taxonomy and schema structure
for converting shopper messages into structured intelligence.

CRITICAL: These values are LOCKED. Do not add new categories.
"""

from typing import TypedDict, Literal
from enum import Enum


# Frozen Taxonomy (DO NOT MODIFY)
class Intent(str, Enum):
    """Why is the shopper talking to us right now?"""
    BROWSING = "browsing"
    PRODUCT_COMPARISON = "product_comparison"
    FIT_VALIDATION = "fit_validation"
    PRICE_EVALUATION = "price_evaluation"
    POLICY_CLARIFICATION = "policy_clarification"
    PURCHASE_READINESS = "purchase_readiness"
    UNKNOWN = "unknown"  # Fallback only


class Objection(str, Enum):
    """What might stop this shopper from buying?"""
    PRICE_SENSITIVITY = "price_sensitivity"
    FIT_UNCERTAINTY = "fit_uncertainty"
    TRUST_QUALITY_CONCERN = "trust_quality_concern"
    DELIVERY_RETURNS_RISK = "delivery_returns_risk"
    CHOICE_OVERLOAD = "choice_overload"
    NONE = "none"


class PurchaseStage(str, Enum):
    """How close is this shopper to checkout?"""
    EARLY = "early"
    CONSIDERATION = "consideration"
    DECISION = "decision"


class Sentiment(str, Enum):
    """What emotional tone is present?"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    ANXIOUS = "anxious"
    HESITANT = "hesitant"


# Schema Contract
class IntelligenceOutput(TypedDict):
    """
    The contract between human language and machine reasoning.
    
    Every shopper message MUST produce exactly ONE instance of this schema.
    """
    intent: str  # Must be value from Intent enum
    objection: str  # Must be value from Objection enum
    purchase_stage: str  # Must be value from PurchaseStage enum
    sentiment: str  # Must be value from Sentiment enum
    confidence: float  # Must be in range [0.0, 1.0]


# Allowed values for quick validation
ALLOWED_INTENTS = {e.value for e in Intent}
ALLOWED_OBJECTIONS = {e.value for e in Objection}
ALLOWED_STAGES = {e.value for e in PurchaseStage}
ALLOWED_SENTIMENTS = {e.value for e in Sentiment}


def get_fallback_output() -> IntelligenceOutput:
    """
    Return the canonical fallback output when classification fails.
    
    This is used when:
    - Classification fails after retry
    - Input is invalid
    - System error occurs
    """
    return {
        "intent": Intent.UNKNOWN.value,
        "objection": Objection.NONE.value,
        "purchase_stage": PurchaseStage.EARLY.value,
        "sentiment": Sentiment.NEUTRAL.value,
        "confidence": 0.0
    }
