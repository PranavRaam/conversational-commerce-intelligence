"""
Schema Validation Module
LEVEL 2 STEP D.2 - Schema Validation

Enforces that outputs match the schema contract exactly.
This validation runs BEFORE business logic enforcement.

CRITICAL: Invalid outputs are REJECTED, not silently fixed.
"""

from typing import Any, Dict, Tuple
from schema import (
    IntelligenceOutput,
    ALLOWED_INTENTS,
    ALLOWED_OBJECTIONS,
    ALLOWED_STAGES,
    ALLOWED_SENTIMENTS
)


class ValidationError(Exception):
    """Raised when schema validation fails."""
    pass


def validate_schema(output: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate that output conforms to IntelligenceOutput schema.
    
    Args:
        output: Dictionary to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        - (True, "") if valid
        - (False, "reason") if invalid
        
    Validation checks:
    1. All required fields exist
    2. Types are correct
    3. Values are from allowed enums
    4. Confidence is in range [0.0, 1.0]
    """
    
    # Check 1: All required fields exist
    required_fields = {"intent", "objection", "purchase_stage", "sentiment", "confidence"}
    missing = required_fields - set(output.keys())
    if missing:
        return False, f"Missing required fields: {missing}"
    
    # Check 2: Extra fields not allowed (strict schema)
    extra = set(output.keys()) - required_fields
    if extra:
        return False, f"Unexpected fields: {extra}"
    
    # Check 3: Type validation
    if not isinstance(output["intent"], str):
        return False, f"intent must be string, got {type(output['intent']).__name__}"
    
    if not isinstance(output["objection"], str):
        return False, f"objection must be string, got {type(output['objection']).__name__}"
    
    if not isinstance(output["purchase_stage"], str):
        return False, f"purchase_stage must be string, got {type(output['purchase_stage']).__name__}"
    
    if not isinstance(output["sentiment"], str):
        return False, f"sentiment must be string, got {type(output['sentiment']).__name__}"
    
    if not isinstance(output["confidence"], (int, float)):
        return False, f"confidence must be numeric, got {type(output['confidence']).__name__}"
    
    # Check 4: Enum membership
    if output["intent"] not in ALLOWED_INTENTS:
        return False, f"intent '{output['intent']}' not in allowed values: {ALLOWED_INTENTS}"
    
    if output["objection"] not in ALLOWED_OBJECTIONS:
        return False, f"objection '{output['objection']}' not in allowed values: {ALLOWED_OBJECTIONS}"
    
    if output["purchase_stage"] not in ALLOWED_STAGES:
        return False, f"purchase_stage '{output['purchase_stage']}' not in allowed values: {ALLOWED_STAGES}"
    
    if output["sentiment"] not in ALLOWED_SENTIMENTS:
        return False, f"sentiment '{output['sentiment']}' not in allowed values: {ALLOWED_SENTIMENTS}"
    
    # Check 5: Confidence range
    confidence = float(output["confidence"])
    if not (0.0 <= confidence <= 1.0):
        return False, f"confidence must be in range [0.0, 1.0], got {confidence}"
    
    return True, ""


def validate_and_raise(output: Dict[str, Any]) -> IntelligenceOutput:
    """
    Validate schema and raise exception if invalid.
    
    Args:
        output: Dictionary to validate
        
    Returns:
        Validated IntelligenceOutput
        
    Raises:
        ValidationError: If schema validation fails
    """
    is_valid, error = validate_schema(output)
    if not is_valid:
        raise ValidationError(f"Schema validation failed: {error}")
    
    return output  # type: ignore
