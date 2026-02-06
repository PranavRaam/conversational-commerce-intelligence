"""
LOCKED CLASSIFICATION PROMPT FOR LLM
LEVEL 2 STEP C - Production System Prompt

This prompt is FROZEN.
Do not modify wording.
Do not add explanations.
Do not change labels.

This prompt is injected into Ollama/LLaMA for every turn.
"""

# System + Task Prompt (LOCKED)
SYSTEM_PROMPT = """You are an AI system that extracts structured shopper intelligence from ecommerce conversations.

Your role is ANALYSIS and CLASSIFICATION, not conversation.
You do NOT speak to the shopper.
You do NOT explain your reasoning.

Your task:
Given a shopper message and the assistant's reply, classify the shopper's intent,
buying objection (if any), purchase stage, sentiment, and confidence.

You MUST follow these rules strictly:

GENERAL RULES:
- Output MUST be valid JSON.
- Output MUST contain ONLY the specified fields.
- Do NOT add explanations, comments, or extra text.
- Do NOT invent new labels.
- Choose the single most dominant intent.
- If no buying objection is present, use "none".
- Be conservative when uncertain.

INTENT DEFINITIONS (choose ONE):
- browsing: The shopper is exploring or discovering products with no commitment.
- product_comparison: The shopper is comparing two or more products or options.
- fit_validation: The shopper is checking size, fit, or physical suitability.
- price_evaluation: The shopper is evaluating cost, value, or price fairness.
- policy_clarification: The shopper is asking about returns, shipping, warranty, or trust policies.
- purchase_readiness: The shopper explicitly signals intent to buy or proceed to checkout.

OBJECTION DEFINITIONS (choose ONE):
- price_sensitivity: Concern that the product is too expensive or not worth the price.
- fit_uncertainty: Concern that the product may not fit or suit them physically.
- trust_quality_concern: Doubts about product quality, durability, or brand trust.
- delivery_returns_risk: Worries about shipping, delivery delays, or return process.
- choice_overload: Difficulty choosing between multiple options.
- none: No explicit buying blocker is present.

PURCHASE STAGES:
- early: Exploration phase, no buying intent yet.
- consideration: Evaluating options, validating details.
- decision: Ready to buy but may have final concerns.

SENTIMENT:
- positive: Confident, excited, or satisfied.
- neutral: Informational or calm tone.
- anxious: Worried, uncertain, or stressed.
- hesitant: Interested but unsure or resistant.

IMPORTANT GUIDANCE:
- If the shopper says "I want to buy", "I'll take it", or similar → intent MUST be purchase_readiness.
- If the shopper expresses worry about size or fit → objection SHOULD be fit_uncertainty.
- Assistant reassurance does NOT remove an objection if the shopper still expressed concern.
- Do not downgrade purchase stage without strong reason.

Return JSON EXACTLY in the following format:

{
  "intent": "",
  "objection": "",
  "purchase_stage": "",
  "sentiment": "",
  "confidence": 0.0
}"""


# User prompt template (dynamically filled per turn)
USER_PROMPT_TEMPLATE = """Shopper Message:
{user_message}

Assistant Reply:
{assistant_reply}"""


def build_classification_prompt(user_message: str, assistant_reply: str = "") -> str:
    """
    Build the complete prompt to send to LLM.
    
    Args:
        user_message: The shopper's message
        assistant_reply: The assistant's response
        
    Returns:
        Complete prompt string (system + user input)
    """
    user_section = USER_PROMPT_TEMPLATE.format(
        user_message=user_message,
        assistant_reply=assistant_reply
    )
    return f"{SYSTEM_PROMPT}\n\n{user_section}"


# Example (for documentation/testing)
EXAMPLE_INPUT = {
    "user_message": "I'm worried it won't fit me. I'm 6 feet tall.",
    "assistant_reply": "It has an oversized fit and we offer free returns."
}

EXAMPLE_OUTPUT = {
    "intent": "fit_validation",
    "objection": "fit_uncertainty",
    "purchase_stage": "consideration",
    "sentiment": "neutral",
    "confidence": 0.75
}

# Why this prompt works
PROMPT_DESIGN_NOTES = """
Why this prompt works:

1. Forces analyst mode, not chat mode
   - "Your role is ANALYSIS and CLASSIFICATION, not conversation"
   - "You do NOT speak to the shopper"

2. Explicitly defines each label
   - No ambiguity about what each value means
   - Shoppers must map to one of 6 intents

3. Anchors edge cases
   - "If the shopper says 'I want to buy'" → intent MUST be purchase_readiness
   - "If the shopper expresses worry about size" → objection SHOULD be fit_uncertainty
   - "Assistant reassurance does NOT remove an objection"

4. Produces stable JSON
   - Exact format specified
   - Required fields locked
   - Data types explicit (string, float)

5. Plays perfectly with business-rule enforcement
   - System corrects remaining edge cases
   - LLM + business logic = deterministic behavior
"""

# Success criteria for prompt lock
PROMPT_VALIDATION_CRITERIA = """
This prompt is LOCKED when:

✓ It produces valid JSON 95%+ of the time
✓ Errors are formatting, not conceptual
✓ Business rules fix remaining edge cases
✓ Stub → LLaMA swap changes nothing downstream

At that point: The LLM part of your project is complete.
"""

# What NOT to do
DO_NOT_INSTRUCTIONS = """
❌ Do not add "Please" or polite language
❌ Do not ask the model to explain reasoning
❌ Do not let it summarize the conversation
❌ Do not change labels casually
❌ Do not let it output markdown or text
❌ Do not add system messages in the middle
❌ Do not include example outputs in dynamic input
"""
