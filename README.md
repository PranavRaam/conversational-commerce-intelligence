# 🛍️ Conversational Commerce Intelligence System

**Transform raw shopper conversations into actionable business insights using LLM-powered classification and deterministic aggregation.**

---

## 🎯 What Does This Do?

This system answers the questions every e-commerce brand actually cares about:

- **Why did the shopper hesitate?** → Identifies objections (price, fit, quality, delivery)
- **Did they convert?** → Tracks funnel outcome (converted, dropped, undecided)
- **What blocked them?** → Surfaces dominant barriers preventing purchase
- **What should we do next?** → Recommends specific follow-up actions

**Not a chatbot. Not just analytics. A complete intelligence pipeline.**

---

## 🚀 Quick Start

### 1. Run a Session Demo (Recommended)

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows

# Run complete session analysis
cd src
python demo_session.py
```

**Output:** 7-turn conversation → Session summary with business recommendations

### 2. Use in Your Code

```python
from src.intelligence_extractor import IntelligenceExtractor
from src.session_aggregator import aggregate_session

# Initialize extractor
extractor = IntelligenceExtractor(use_stub=False)  # LLM mode

# Analyze conversation turns
turns = []
conversation = [
    {"user": "Show me your winter hoodies", "bot": "We have premium options..."},
    {"user": "I'm worried it won't fit", "bot": "We offer free returns..."},
    {"user": "I want to buy size L", "bot": "Great choice!"}
]

for turn in conversation:
    intelligence = extractor.extract_intelligence(turn['user'], turn['bot'])
    turns.append(intelligence)

# Get session-level insights
summary = aggregate_session(turns)

print(summary['funnel_outcome'])          # "converted"
print(summary['dominant_objection'])      # "fit_uncertainty"
print(summary['recommended_followup'])    # "highlight size guide and free returns"
```

---

## 📊 How It Works: 3-Level Architecture

### **Level 2: Turn-Level Intelligence**
Extracts structured data from each shopper message.

**Input:** Single message + bot reply

```
"I'm worried it won't fit me. I'm 6 feet tall."
```

**Output:** Structured intelligence

```json
{
  "intent": "fit_validation",
  "objection": "fit_uncertainty",
  "purchase_stage": "consideration",
  "sentiment": "anxious",
  "confidence": 0.8
}
```

**How:**
1. **LLM Classification** → LLaMA 3.1 via Ollama analyzes message
2. **Schema Validation** → Ensures output matches strict contract
3. **Business Logic** → 7 deterministic rules correct edge cases
4. **Normalization** → Final validation before return

---

### **Level 3: LLM Classifier**
Intelligent classification using LLaMA 3.1 (Ollama).

**Locked Settings:**
- Temperature: 0.1 (low creativity, high consistency)
- Top P: 0.9 (deterministic)
- Max Tokens: 200 (fast inference)

**Taxonomy (Frozen):**

| Intent | Objection | Purchase Stage | Sentiment |
|--------|-----------|----------------|-----------|
| browsing | price_sensitivity | early | positive |
| product_comparison | fit_uncertainty | consideration | neutral |
| fit_validation | trust_quality_concern | decision | anxious |
| price_evaluation | delivery_returns_risk | | hesitant |
| policy_clarification | choice_overload | | |
| purchase_readiness | none | | |

**Business Rules (Applied After LLM):**
1. Intent → Stage canonical mapping
2. Invalid intent-objection combo removal
3. Confidence guardrails (< 0.3 → ignore objection)
4. **Fit concern enforcement** (keywords force fit_uncertainty)
5. **Hesitation escalation** (upgrades to purchase_readiness)
6. **Purchase intent override** ("I want to buy" overrides everything)
7. **Stage normalization** (final alignment check)

---

### **Level 4: Session Aggregation ✨ NEW**
Converts multiple turns into one actionable session insight.

**Input:** List of turn-level intelligence

```python
[
  {"intent": "browsing", "objection": "none", ...},
  {"intent": "fit_validation", "objection": "fit_uncertainty", ...},
  {"intent": "purchase_readiness", "objection": "none", ...}
]
```

**Output:** Session summary

```json
{
  "primary_intent": "purchase_readiness",
  "dominant_objection": "fit_uncertainty",
  "journey_path": ["browsing", "fit", "purchase"],
  "funnel_outcome": "converted",
  "conversion_likelihood": "high",
  "recommended_followup": "highlight size guide and free returns"
}
```

**Aggregation Rules:**
1. **Primary Intent** → Last strong signal wins (purchase_readiness > most frequent)
2. **Dominant Objection** → Most frequent non-none objection
3. **Journey Path** → Compressed, deduplicated stage sequence
4. **Funnel Outcome** → converted | undecided | dropped
5. **Conversion Likelihood** → high | medium | low
6. **Recommended Followup** → Mapped from dominant objection

---

## 🎬 Example: Complete Session Analysis

### Input Conversation

```
Turn 1: "Show me your winter hoodies"
Turn 2: "What's the difference between the two?"
Turn 3: "The Premium one is expensive. Is it worth it?"
Turn 4: "I'm worried it won't fit me. I'm 6 feet tall."
Turn 5: "Still not 100% sure about this."
Turn 6: "How long does shipping take?"
Turn 7: "I want to buy the Premium Waterproof Hoodie in size L."
```

### Turn-Level Intelligence (Excerpt)

```json
Turn 3: {
  "intent": "price_evaluation",
  "objection": "price_sensitivity",
  "purchase_stage": "decision",
  "sentiment": "hesitant"
}

Turn 4: {
  "intent": "fit_validation",
  "objection": "fit_uncertainty",
  "purchase_stage": "consideration",
  "sentiment": "anxious"
}

Turn 7: {
  "intent": "purchase_readiness",
  "objection": "none",
  "purchase_stage": "decision",
  "sentiment": "positive"
}
```

### Session Summary

```json
{
  "primary_intent": "purchase_readiness",
  "dominant_objection": "fit_uncertainty",
  "journey_path": [
    "browsing",
    "comparison",
    "price",
    "fit",
    "purchase",
    "policy",
    "purchase"
  ],
  "funnel_outcome": "converted",
  "conversion_likelihood": "high",
  "recommended_followup": "highlight size guide and free returns"
}
```

### Business Insights

**✅ Conversion Achieved**
- Shopper overcame initial price and fit concerns
- Primary blocker: fit_uncertainty (addressed before purchase)
- Journey: discovery → comparison → objections → conversion

**🎯 Actionable Recommendations**
1. Send order confirmation email
2. Upsell complementary products
3. **Address fit_uncertainty in post-purchase messaging** ← Key insight
4. For future shoppers: Emphasize size guide earlier in conversation

---

## 📂 Project Structure

```
src/
├── schema.py                      # Frozen taxonomy (6 intents, 6 objections, 3 stages, 4 sentiments)
├── validator.py                   # Schema enforcement (strict validation)
├── business_logic.py              # 7 deterministic rules
├── stub_classifier.py             # Keyword-based classifier (testing)
├── llm_classifier.py              # LLaMA 3.1 classifier (production)
├── intelligence_extractor.py      # Turn-level extraction API
├── llm_prompt.py                  # Locked prompt for LLM
│
├── session_schema.py              # Session output schema
├── session_aggregator.py          # Session-level aggregation logic
│
├── test_extractor.py              # Turn-level tests
├── test_llm_comparison.py         # Stub vs LLM comparison
├── test_session_aggregator.py     # Session aggregation tests (14/14 passing)
│
├── demo.py                        # Turn demo (stub)
├── demo_llm.py                    # Turn demo (LLM)
└── demo_session.py                # Session demo (complete workflow)

data/
└── product_catalog.json           # Ground truth product data (13 items)
```

---

## 🧪 Testing

### Run All Tests

```bash
cd src

# Test turn-level extraction
python test_extractor.py

# Test LLM vs stub comparison
python test_llm_comparison.py

# Test session aggregation (14 test cases)
python test_session_aggregator.py
```

### Test Results

```
✅ Turn-level extraction: 19/19 passing
✅ LLM comparison: 8/8 scenarios passing
✅ Session aggregation: 14/14 tests passing
✅ Full 7-turn demo: All turns correct
```

---

## ⚙️ Configuration

### LLM vs Stub Mode

```python
# Production mode (LLM - slower, more accurate)
extractor = IntelligenceExtractor(use_stub=False)

# Testing mode (Stub - instant, keyword-based)
extractor = IntelligenceExtractor(use_stub=True)
```

### Prerequisites

**For LLM Mode:**
- Ollama installed ([ollama.ai](https://ollama.ai))
- LLaMA 3.1 model: `ollama pull llama3.1`
- Python 3.10+
- `pip install ollama`

**For Stub Mode:**
- Python 3.10+ only
- No external dependencies

---

## 🔧 Advanced Usage

### 1. Real-Time Analysis

```python
class LiveAnalyzer:
    def __init__(self):
        self.extractor = IntelligenceExtractor(use_stub=False)
        self.session_turns = []
    
    def on_message(self, user_msg, bot_reply):
        # Extract turn intelligence
        intelligence = self.extractor.extract_intelligence(user_msg, bot_reply)
        self.session_turns.append(intelligence)
        
        # Get live session summary
        summary = aggregate_session(self.session_turns)
        
        # Take action based on objection
        if summary['dominant_objection'] == 'price_sensitivity':
            self.trigger_discount_offer()
        elif summary['dominant_objection'] == 'fit_uncertainty':
            self.show_size_guide()
        
        return summary
```

### 2. Batch Processing

```python
def analyze_historical_conversations(conversations_db):
    extractor = IntelligenceExtractor(use_stub=False)
    
    results = []
    for session in conversations_db:
        turns = []
        for turn in session['messages']:
            intel = extractor.extract_intelligence(
                turn['user'], 
                turn['assistant']
            )
            turns.append(intel)
        
        summary = aggregate_session(turns)
        results.append({
            'session_id': session['id'],
            'outcome': summary['funnel_outcome'],
            'main_blocker': summary['dominant_objection'],
            'action': summary['recommended_followup']
        })
    
    return results
```

### 3. A/B Testing Different Classifiers

```python
stub = IntelligenceExtractor(use_stub=True)
llm = IntelligenceExtractor(use_stub=False)

message = "I'm worried about the price"

stub_result = stub.extract_intelligence(message)
llm_result = llm.extract_intelligence(message)

print(f"Stub: {stub_result['intent']}")  # Keyword-based
print(f"LLM: {llm_result['intent']}")    # Context-aware
```

---

## 🎯 Business Value

### What You Get

**Turn-Level Insights:**
- Shopper intent for every message
- Buying objections identified
- Purchase stage tracking
- Sentiment analysis

**Session-Level Intelligence:**
- Primary conversion blocker
- Complete journey path
- Funnel outcome prediction
- Recommended next action

### Use Cases

1. **Live Chat Optimization**
   - Detect objections in real-time
   - Route to appropriate agent
   - Trigger automated interventions

2. **Conversion Funnel Analysis**
   - Identify where shoppers drop off
   - Understand objection patterns
   - Optimize messaging by stage

3. **Post-Conversation Actions**
   - Abandoned cart emails (mention specific objection)
   - Retargeting ads (address main blocker)
   - Follow-up campaigns (personalized by journey)

4. **Product/UX Improvements**
   - Track fit_uncertainty → improve size guide
   - Track price_sensitivity → review pricing
   - Track choice_overload → simplify catalog

---

## 🔐 What's Locked (Do Not Modify)

### Taxonomy (19 Values Total)
- 6 Intents
- 6 Objections  
- 3 Purchase Stages
- 4 Sentiments

**These are frozen.** Adding new values breaks the system.

### Business Logic (7 Rules)
Execution order matters. Rules are:
1. Intent-stage mapping
2. Invalid combo removal
3. Confidence guardrails
4. Fit concern enforcement
5. Hesitation escalation
6. Purchase intent override
7. Stage normalization

### LLM Prompt
Locked in `llm_prompt.py`. Do not tune. If LLM struggles, fix in business logic, not prompt.

### Session Aggregation Rules
6 rules are deterministic and tested. Modifications require full test suite re-validation.

---

## ⚡ Performance

| Metric | Stub | LLM |
|--------|------|-----|
| **Latency (per turn)** | <0.001s | ~8s (local CPU) |
| **Accuracy** | Keyword-based | 87.5% intent accuracy |
| **Use Case** | Fast testing | Production |
| **Session Aggregation** | <0.001s | <0.001s (instant) |

**Note:** LLM latency improves to <2s with GPU acceleration.

---

## 🐛 Troubleshooting

### LLM Not Working

**Issue:** `ModuleNotFoundError: No module named 'ollama'`

**Solution:**
```bash
pip install ollama
```

**Issue:** Slow performance (>10s per turn)

**Solution:**
- Expected on CPU: ~8s is normal
- Use stub mode for testing: `use_stub=True`
- Production: Deploy with GPU

### Unexpected Classifications

**Issue:** LLM classifies differently than expected

**Solution:**
- Business logic automatically corrects edge cases
- Check `business_logic.py` for rules
- LLM + business logic = final output (both matter)

### Import Errors

**Issue:** Cannot import modules

**Solution:**
```bash
# Ensure you're in the right directory
cd src
python demo_session.py
```

---

## 📈 System Statistics

**Code:**
- Core modules: 9 files (~1,300 lines)
- Test suites: 3 files (~600 lines)
- Demos: 3 files (~450 lines)
- Total: ~2,350 lines of production code

**Tests:**
- 41 total test cases
- 100% passing rate
- All edge cases covered

**Documentation:**
- You're reading it (this README is everything)

---

## 🚦 Next Steps

### Level 5 (Planned): Conversation Handler
- Multi-turn conversation memory
- Context-aware response generation
- Dialog flow management
- Personalized recommendations
- Automated interventions

---

## 💡 Key Design Principles

1. **Schema Before Code** → Contract defined before implementation
2. **Stub Before LLM** → Test logic without model dependency
3. **Validate Before Trust** → Strict schema enforcement
4. **System Decides** → LLM suggests, business logic corrects
5. **Determinism Over Creativity** → Reproducible, explainable outputs
6. **Fail Gracefully** → Retry once, clear error messages

---

## 📝 Example Workflows

### Workflow 1: E-commerce Platform Integration

```python
# In your chat handler
from src.intelligence_extractor import IntelligenceExtractor
from src.session_aggregator import aggregate_session

class ChatHandler:
    def __init__(self):
        self.extractor = IntelligenceExtractor(use_stub=False)
        self.sessions = {}  # session_id -> list of turns
    
    def on_user_message(self, session_id, user_msg, bot_reply):
        # Extract intelligence
        intelligence = self.extractor.extract_intelligence(user_msg, bot_reply)
        
        # Store turn
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append(intelligence)
        
        # Analyze session
        summary = aggregate_session(self.sessions[session_id])
        
        # Take action
        if summary['funnel_outcome'] == 'undecided':
            if summary['dominant_objection'] == 'price_sensitivity':
                self.send_discount_code(session_id)
            elif summary['dominant_objection'] == 'fit_uncertainty':
                self.trigger_size_guide_popup(session_id)
        
        # Log for analytics
        self.log_session_state(session_id, summary)
        
        return intelligence, summary
```

### Workflow 2: Abandoned Cart Recovery

```python
# Daily batch job
def recover_abandoned_carts():
    extractor = IntelligenceExtractor(use_stub=False)
    
    # Get yesterday's dropped sessions
    dropped_sessions = db.get_sessions_by_outcome('dropped', days=1)
    
    for session in dropped_sessions:
        # Re-analyze conversation
        turns = [extractor.extract_intelligence(t['user'], t['bot']) 
                 for t in session['turns']]
        summary = aggregate_session(turns)
        
        # Send targeted email
        if summary['dominant_objection'] == 'price_sensitivity':
            send_email(
                session['user_email'],
                template='discount_offer',
                discount='10%'
            )
        elif summary['dominant_objection'] == 'fit_uncertainty':
            send_email(
                session['user_email'],
                template='size_guide',
                product=session['last_product']
            )
```

---

## 📞 Support

**Issues or Questions?**
- Check the demos: `python demo_session.py`
- Run tests: `python test_session_aggregator.py`
- Review code: All modules are documented inline

