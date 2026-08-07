"""
BrainTrader
------------------------
Confluence Engine Test
"""

from confluence_engine import calculate_confluence



# --------------------------------
# Sample BrainTrader outputs
# --------------------------------


structure = {

    "trend": "BULLISH"

}



bos = {

    "type": "BULLISH"

}



choch = {

    "type": "BULLISH"

}



liquidity = {

    "bullish": [

        {

            "level": 1305,

            "quality": 85

        }

    ],

    "bearish": []

}



support_resistance = {

    "nearest_support": 1300,

    "nearest_resistance": 1350

}



indicator = {

    "score": 80

}




# --------------------------------
# Calculate
# --------------------------------


result = calculate_confluence(

    structure=structure,

    bos=bos,

    choch=choch,

    liquidity=liquidity,

    support_resistance=support_resistance,

    indicator=indicator

)



print()

print("=" * 60)

print("BRAINTRADER CONFLUENCE TEST")

print("=" * 60)



print()

print(
    "Score    :",
    result["score"]
)


print(
    "Decision :",
    result["decision"]
)



print()

print("Reasons")

print("-" * 30)


for reason in result["reasons"]:

    print(
        "-",
        reason
    )