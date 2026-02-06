from typing import Dict
from schema import (
    IntelligenceOutput,
    Intent,
    Objection,
    PurchaseStage,
    Sentiment
)


# PART 1: Intent → Allowed Purchase Stage Mapping (CANONICAL)
INTENT_STAGE_MAPPING = {
    Intent.BROWSING.value: [PurchaseStage.EARLY.value],
    Intent.POLICY_CLARIFICATION.value: [PurchaseStage.EARLY.value, PurchaseStage.CONSIDERATION.value],
    Intent.PRODUCT_COMPARISON.value: [PurchaseStage.CONSIDERATION.value],
    Intent.FIT_VALIDATION.value: [PurchaseStage.CONSIDERATION.value, PurchaseStage.DECISION.value],
    Intent.PRICE_EVALUATION.value: [PurchaseStage.DECISION.value],
    Intent.PURCHASE_READINESS.value: [PurchaseStage.DECISION.value],
    Intent.UNKNOWN.value: [PurchaseStage.EARLY.value]  # Fallback
}


# PART 3: Invalid Intent + Objection Combinations
INVALID_INTENT_OBJECTION_COMBOS = {
    # Browsing phase: user hasn't committed to product yet
    (Intent.BROWSING.value, Objection.PRICE_SENSITIVITY.value),
    (Intent.BROWSING.value, Objection.FIT_UNCERTAINTY.value),
    
    # Policy questions are informational, not product-specific
    (Intent.POLICY_CLARIFICATION.value, Objection.CHOICE_OVERLOAD.value),
    
    # Purchase readiness with no objection is rare (usually friction exists)
    # We allow this but track it as unusual
}


# PART 5: Confidence-Based Guardrails
CONFIDENCE_THRESHOLD_LOW = 0.5
CONFIDENCE_THRESHOLD_VERY_LOW = 0.3


# PART 6: Keyword-Based Override Rules
FIT_CONCERN_KEYWORDS = {
    "worried", "not sure", "won't fit", "will it fit", "size issue",
    "too small", "too big", "fit me", "6 feet", "between", "concern"
}

HESITATION_KEYWORDS = {
    "not sure", "still not", "unsure", "hesitant", "maybe", "idk",
    "not 100%", "not completely"
}

PURCHASE_INTENT_KEYWORDS = {
    "i want to buy", "i'll take", "i will buy", "add to cart",
    "checkout", "place order", "buy now", "want to buy", "i want"
}

# Intent → Stage Mapping (for final normalization)
INTENT_STAGE_MAP = {
    Intent.BROWSING.value: PurchaseStage.EARLY.value,
    Intent.PRODUCT_COMPARISON.value: PurchaseStage.CONSIDERATION.value,
    Intent.FIT_VALIDATION.value: PurchaseStage.CONSIDERATION.value,
    Intent.POLICY_CLARIFICATION.value: PurchaseStage.CONSIDERATION.value,
    Intent.PRICE_EVALUATION.value: PurchaseStage.DECISION.value,
    Intent.PURCHASE_READINESS.value: PurchaseStage.DECISION.value,
    Intent.UNKNOWN.value: PurchaseStage.EARLY.value
}


def enforce_business_logic(output: IntelligenceOutput, user_message: str = "") -> IntelligenceOutput:
    """
    Apply deterministic business rules to correct LLM output.
    
    CRITICAL: Order matters! Rules run in this sequence:
    1. Basic intent-stage mapping
    2. Invalid combo corrections
    3. Confidence guardrails
    4. Fit concern enforcement (keyword-based)
    5. Residual hesitation enforcement (keyword-based)
    6. Purchase readiness enforcement (keyword-based)
    7. Final stage normalization
    
    Args:
        output: Validated schema output from LLM or stub
        user_message: Original user message (for keyword-based rules)
        
    Returns:
        Corrected IntelligenceOutput with business rules applied
    """
    
    # Make a mutable copy
    corrected = dict(output)
    
    # RULE 1: Intent → Stage Alignment
    corrected = _enforce_intent_stage_mapping(corrected)
    
    # RULE 2: Invalid Intent–Objection Combinations
    corrected = _enforce_intent_objection_rules(corrected)
    
    # RULE 3: Confidence-Based Overrides
    corrected = _apply_confidence_guardrails(corrected)
    
    # RULE 4: Fit Concern Enforcement (keyword-based)
    if user_message:
        corrected = _enforce_fit_objection(user_message, corrected)
    
    # RULE 5: Residual Hesitation Enforcement (keyword-based)
    if user_message:
        corrected = _enforce_residual_hesitation(user_message, corrected)
    
    # RULE 6: Purchase Readiness Enforcement (keyword-based, overrides everything)
    if user_message:
        corrected = _enforce_purchase_readiness(user_message, corrected)
    
    # RULE 7: Final Stage Normalization (ensures intent-stage alignment)
    corrected = _normalize_purchase_stage(corrected)
    
    return corrected  # type: ignore


def _enforce_intent_stage_mapping(output: Dict) -> Dict:
    """
    Enforce that purchase_stage matches allowed stages for the intent.
    
    If stage is outside allowed bounds → override to canonical stage.
    """
    intent = output["intent"]
    current_stage = output["purchase_stage"]
    
    allowed_stages = INTENT_STAGE_MAPPING.get(intent, [PurchaseStage.EARLY.value])
    
    if current_stage not in allowed_stages:
        # Override to first allowed stage (canonical default)
        output["purchase_stage"] = allowed_stages[0]
    
    return output


def _enforce_intent_objection_rules(output: Dict) -> Dict:
    """
    Remove objections that don't make sense for the given intent.
    
    Invalid combinations → set objection to "none"
    """
    intent = output["intent"]
    objection = output["objection"]
    
    if (intent, objection) in INVALID_INTENT_OBJECTION_COMBOS:
        output["objection"] = Objection.NONE.value
    
    return output


def _apply_confidence_guardrails(output: Dict) -> Dict:
    """
    Apply confidence-based data quality rules.
    
    Rules:
    - confidence < 0.3 → ignore objection (too uncertain)
    - confidence < 0.5 → could mark as low_reliability (future)
    """
    confidence = output["confidence"]
    
    # Very low confidence: ignore objection
    if confidence < CONFIDENCE_THRESHOLD_VERY_LOW:
        output["objection"] = Objection.NONE.value
    
    # Low confidence: keep data but flag (future: add metadata)
    # For now, we just let it pass but could add reliability flag
    
    return output


def get_objection_risk_type(objection: str) -> str:
    """
    Map objection to risk type (for future analytics/actions).
    
    This is not stored yet but guides system understanding.
    """
    risk_mapping = {
        Objection.PRICE_SENSITIVITY.value: "value_risk",
        Objection.FIT_UNCERTAINTY.value: "return_risk",
        Objection.TRUST_QUALITY_CONCERN.value: "brand_risk",
        Objection.DELIVERY_RETURNS_RISK.value: "logistics_risk",
        Objection.CHOICE_OVERLOAD.value: "decision_paralysis",
        Objection.NONE.value: "no_risk"
    }
    return risk_mapping.get(objection, "unknown_risk")


def _enforce_fit_objection(user_message: str, output: Dict) -> Dict:
    """
    FIX 1: Fit concern should ALWAYS create fit_uncertainty.
    
    Assistant reassurance does NOT remove the objection.
    It may reduce sentiment intensity, but not the blocker.
    """
    text = user_message.lower()
    
    if output["intent"] == Intent.FIT_VALIDATION.value:
        if any(k in text for k in FIT_CONCERN_KEYWORDS):
            output["objection"] = Objection.FIT_UNCERTAINTY.value
    
    return output


def _enforce_residual_hesitation(user_message: str, output: Dict) -> Dict:
    """
    FIX 2: Residual hesitation ≠ product comparison.
    
    If the user expresses hesitation without comparing options,
    it is late-funnel doubt, not comparison.
    
    Escalates browsing, product_comparison, OR fit_validation with hesitation
    to purchase_readiness + decision stage.
    """
    text = user_message.lower()
    
    if any(k in text for k in HESITATION_KEYWORDS):
        if output["intent"] in {
            Intent.PRODUCT_COMPARISON.value,
            Intent.BROWSING.value,
            Intent.FIT_VALIDATION.value
        }:
            output["intent"] = Intent.PURCHASE_READINESS.value
            output["purchase_stage"] = PurchaseStage.DECISION.value
            
            # If no specific objection, assume fit uncertainty
            if output["objection"] == Objection.NONE.value:
                output["objection"] = Objection.FIT_UNCERTAINTY.value
    
    return output


def _enforce_purchase_readiness(user_message: str, output: Dict) -> Dict:
    """
    FIX 3: Explicit buy intent must override everything.
    
    This is non-negotiable for analytics correctness.
    """
    text = user_message.lower()
    
    if any(k in text for k in PURCHASE_INTENT_KEYWORDS):
        output["intent"] = Intent.PURCHASE_READINESS.value
        output["purchase_stage"] = PurchaseStage.DECISION.value
        
        # Objection only remains if explicitly stated
        if output["objection"] not in {
            Objection.PRICE_SENSITIVITY.value,
            Objection.DELIVERY_RETURNS_RISK.value,
            Objection.FIT_UNCERTAINTY.value
        }:
            output["objection"] = Objection.NONE.value
        
        output["sentiment"] = Sentiment.POSITIVE.value
    
    return output


def _normalize_purchase_stage(output: Dict) -> Dict:
    """
    FIX 4: Enforce intent → stage mapping AFTER all rules.
    
    This ensures:
    - No browsing → decision bugs
    - No purchase_readiness → consideration bugs
    """
    intent = output["intent"]
    output["purchase_stage"] = INTENT_STAGE_MAP.get(intent, PurchaseStage.EARLY.value)
    return output


def get_recommended_action(objection: str) -> str:
    """
    Map objection to recommended system response strategy.
    
    Not implemented yet but defines the mapping for future use.
    """
    action_mapping = {
        Objection.PRICE_SENSITIVITY.value: "value_justification",
        Objection.FIT_UNCERTAINTY.value: "reassurance_and_returns",
        Objection.TRUST_QUALITY_CONCERN.value: "social_proof_warranty",
        Objection.DELIVERY_RETURNS_RISK.value: "policy_clarity",
        Objection.CHOICE_OVERLOAD.value: "guided_recommendation",
        Objection.NONE.value: "continue_conversation"
    }
    return action_mapping.get(objection, "default_response")
