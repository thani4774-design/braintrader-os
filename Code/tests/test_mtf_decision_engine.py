from market_structure.mtf_decision_engine import (
    calculate_alignment,
    make_decision,
    generate_reason
)

results = {

    "MACRO_15Y": {
        "trend": "BULLISH_TRANSITION"
    },

    "MAJOR_5Y": {
        "trend": "BEARISH"
    },

    "CURRENT_2Y": {
        "trend": "BULLISH_TRANSITION"
    },

    "ENTRY_6M": {
        "trend": "BULLISH"
    }

}

print("=" * 50)
print("MTF DECISION ENGINE TEST")
print("=" * 50)

alignment = calculate_alignment(results)

print("\nAlignment")
print(alignment)

decision = make_decision(
    score=63,
    alignment=alignment["alignment"]
)

print("\nDecision")
print(decision)

print("\nReasons")

for reason in generate_reason(results):
    print("-", reason)