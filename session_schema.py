"""
SESSION SUMMARY SCHEMA
LEVEL 4: Session-Level Aggregation

Defines the output structure for aggregated session intelligence.
This is what brands care about: actionable session insights.
"""

from typing import TypedDict, List, Literal


# Session Output Schema (FROZEN)
class SessionSummary(TypedDict):
    """
    Aggregated session intelligence from multiple turns.
    
    This is the final artifact for business decision-making.
    """
    primary_intent: str  # The dominant intent across all turns
    dominant_objection: str  # The main blocker preventing conversion
    journey_path: List[str]  # Compressed sequence of stages
    funnel_outcome: Literal["converted", "dropped", "undecided"]  # Final state
    conversion_likelihood: Literal["low", "medium", "high"]  # Probability of conversion
    recommended_followup: str  # Actionable next step


# Allowed values (for validation)
ALLOWED_FUNNEL_OUTCOMES = {"converted", "dropped", "undecided"}
ALLOWED_CONVERSION_LIKELIHOOD = {"low", "medium", "high"}

# Intent to Journey Stage Mapping
INTENT_TO_STAGE = {
    "browsing": "browsing",
    "product_comparison": "comparison",
    "price_evaluation": "price",
    "fit_validation": "fit",
    "policy_clarification": "policy",
    "purchase_readiness": "purchase",
    "unknown": "browsing"  # Fallback
}

# Objection to Follow-Up Recommendation Mapping
FOLLOWUP_MAP = {
    "fit_uncertainty": "highlight size guide and free returns",
    "price_sensitivity": "emphasize value and durability",
    "delivery_returns_risk": "reassure shipping speed and easy returns",
    "trust_quality_concern": "show reviews and quality guarantees",
    "choice_overload": "recommend a best-fit option",
    "none": "nudge checkout or show limited-time offer"
}


def validate_session_summary(summary: dict) -> tuple[bool, str]:
    """
    Validate session summary against schema.
    
    Args:
        summary: Session summary dictionary
        
    Returns:
        (is_valid, error_message)
    """
    required_fields = [
        "primary_intent",
        "dominant_objection",
        "journey_path",
        "funnel_outcome",
        "conversion_likelihood",
        "recommended_followup"
    ]
    
    # Check required fields
    for field in required_fields:
        if field not in summary:
            return False, f"Missing required field: {field}"
    
    # Validate types
    if not isinstance(summary["primary_intent"], str):
        return False, "primary_intent must be string"
    
    if not isinstance(summary["dominant_objection"], str):
        return False, "dominant_objection must be string"
    
    if not isinstance(summary["journey_path"], list):
        return False, "journey_path must be array"
    
    # Validate enum values
    if summary["funnel_outcome"] not in ALLOWED_FUNNEL_OUTCOMES:
        return False, f"funnel_outcome must be one of {ALLOWED_FUNNEL_OUTCOMES}"
    
    if summary["conversion_likelihood"] not in ALLOWED_CONVERSION_LIKELIHOOD:
        return False, f"conversion_likelihood must be one of {ALLOWED_CONVERSION_LIKELIHOOD}"
    
    return True, ""
