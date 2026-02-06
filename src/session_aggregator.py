"""
SESSION AGGREGATOR
LEVEL 4: Session-Level Intelligence Aggregation

Converts multiple turn-level intelligence objects into one actionable session insight.

This is pure reasoning + aggregation. No LLM needed.
"""

from typing import List, Dict
from session_schema import (
    SessionSummary,
    INTENT_TO_STAGE,
    FOLLOWUP_MAP,
    validate_session_summary
)


def get_primary_intent(turns: List[Dict]) -> str:
    """
    Determine the primary intent across all turns.
    
    Rule: Last strong signal wins.
    - If purchase_readiness appears → primary intent = purchase_readiness
    - Else → most frequent intent
    
    Args:
        turns: List of turn-level intelligence outputs
        
    Returns:
        Primary intent string
    """
    if not turns:
        return "unknown"
    
    # If purchase_readiness appears, that's the primary intent
    if any(t["intent"] == "purchase_readiness" for t in turns):
        return "purchase_readiness"
    
    # Otherwise, return most frequent intent
    intents = [t["intent"] for t in turns]
    return max(
        set(intents),
        key=lambda i: intents.count(i)
    )


def get_dominant_objection(turns: List[Dict]) -> str:
    """
    Determine the dominant objection blocking conversion.
    
    Rule: Persistence matters.
    - Ignore "none"
    - Choose most frequent non-none objection
    - If tie → choose the latest
    
    Args:
        turns: List of turn-level intelligence outputs
        
    Returns:
        Dominant objection string
    """
    if not turns:
        return "none"
    
    # Filter out "none" objections
    objections = [t["objection"] for t in turns if t["objection"] != "none"]
    
    if not objections:
        return "none"
    
    # Return most frequent objection (latest in case of tie)
    return max(set(objections), key=objections.count)


def get_journey_path(turns: List[Dict]) -> List[str]:
    """
    Create compressed journey path from intents.
    
    Rule:
    - Map intents to journey stages
    - Preserve order
    - Remove consecutive duplicates
    
    Args:
        turns: List of turn-level intelligence outputs
        
    Returns:
        List of journey stage labels
    """
    if not turns:
        return []
    
    path = []
    for turn in turns:
        intent = turn["intent"]
        stage = INTENT_TO_STAGE.get(intent, "browsing")
        
        # Add stage only if different from last
        if not path or path[-1] != stage:
            path.append(stage)
    
    return path


def get_funnel_outcome(turns: List[Dict]) -> str:
    """
    Determine final funnel outcome.
    
    Rule:
    - If purchase_readiness appears → converted
    - Else if decision stage reached → undecided
    - Else → dropped
    
    Args:
        turns: List of turn-level intelligence outputs
        
    Returns:
        Funnel outcome: "converted", "dropped", or "undecided"
    """
    if not turns:
        return "dropped"
    
    # If purchase_readiness intent appears, shopper converted
    if any(t["intent"] == "purchase_readiness" for t in turns):
        return "converted"
    
    # If decision stage reached but no purchase readiness, undecided
    if any(t["purchase_stage"] == "decision" for t in turns):
        return "undecided"
    
    # Otherwise, dropped early
    return "dropped"


def get_conversion_likelihood(turns: List[Dict], dominant_objection: str) -> str:
    """
    Estimate conversion likelihood.
    
    Rule:
    - If purchase_readiness appears → high
    - Else if objection present → medium
    - Else → low
    
    Args:
        turns: List of turn-level intelligence outputs
        dominant_objection: The dominant objection
        
    Returns:
        Conversion likelihood: "low", "medium", or "high"
    """
    if not turns:
        return "low"
    
    # If purchase readiness intent appears, high likelihood
    if any(t["intent"] == "purchase_readiness" for t in turns):
        return "high"
    
    # If objection exists, medium likelihood (needs handling)
    if dominant_objection != "none":
        return "medium"
    
    # Otherwise, low likelihood
    return "low"


def get_followup(dominant_objection: str) -> str:
    """
    Get recommended follow-up action based on objection.
    
    Args:
        dominant_objection: The dominant objection
        
    Returns:
        Recommended follow-up action string
    """
    return FOLLOWUP_MAP.get(dominant_objection, FOLLOWUP_MAP["none"])


def aggregate_session(turns: List[Dict]) -> SessionSummary:
    """
    Aggregate multiple turn-level intelligence objects into session summary.
    
    This is the LEVEL 4 main function.
    
    Args:
        turns: List of turn-level intelligence outputs from Level 2/3
        
    Returns:
        SessionSummary with aggregated insights
        
    Example:
        >>> turns = [
        ...     {"intent": "browsing", "objection": "none", ...},
        ...     {"intent": "fit_validation", "objection": "fit_uncertainty", ...},
        ...     {"intent": "purchase_readiness", "objection": "none", ...}
        ... ]
        >>> summary = aggregate_session(turns)
        >>> print(summary["funnel_outcome"])
        "converted"
    """
    if not turns:
        # Return minimal fallback summary
        return SessionSummary(
            primary_intent="unknown",
            dominant_objection="none",
            journey_path=[],
            funnel_outcome="dropped",
            conversion_likelihood="low",
            recommended_followup="nudge checkout or show limited-time offer"
        )
    
    # Step 1: Get primary intent
    primary_intent = get_primary_intent(turns)
    
    # Step 2: Get dominant objection
    dominant_objection = get_dominant_objection(turns)
    
    # Step 3: Build journey path
    journey_path = get_journey_path(turns)
    
    # Step 4: Determine funnel outcome
    funnel_outcome = get_funnel_outcome(turns)
    
    # Step 5: Estimate conversion likelihood
    conversion_likelihood = get_conversion_likelihood(turns, dominant_objection)
    
    # Step 6: Get recommended follow-up
    recommended_followup = get_followup(dominant_objection)
    
    # Construct summary
    summary = SessionSummary(
        primary_intent=primary_intent,
        dominant_objection=dominant_objection,
        journey_path=journey_path,
        funnel_outcome=funnel_outcome,
        conversion_likelihood=conversion_likelihood,
        recommended_followup=recommended_followup
    )
    
    # Validate before returning
    is_valid, error = validate_session_summary(summary)
    if not is_valid:
        raise ValueError(f"Invalid session summary: {error}")
    
    return summary
