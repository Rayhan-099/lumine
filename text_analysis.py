def analyze_text(text: str):
    """
    Simple rule-based text symptom analyzer for demo.
    """
    t = text.lower()

    if any(k in t for k in ["pimple", "acne", "whitehead", "blackhead"]):
        return {
            "possible_condition": "Acne",
            "causes": "Clogged pores and excess oil production.",
            "suggestion": "Use oil-free cleanser and avoid touching face frequently.",
            "seriousness_level": "low"
        }
    elif any(k in t for k in ["itch", "rash", "allergy"]):
        return {
            "possible_condition": "Allergic Rash / Dermatitis",
            "causes": "Reaction to allergens, soaps, or fabrics.",
            "suggestion": "Use mild moisturizer, avoid scratching, keep skin clean.",
            "seriousness_level": "medium"
        }
    elif any(k in t for k in ["dry", "scaly", "flaky"]):
        return {
            "possible_condition": "Dry Skin / Psoriasis",
            "causes": "Loss of skin moisture or chronic condition.",
            "suggestion": "Apply moisturizers; avoid hot showers and harsh soaps.",
            "seriousness_level": "medium"
        }
    elif any(k in t for k in ["mole", "bleeding", "melanoma", "spot changing"]):
        return {
            "possible_condition": "Suspicious Mole / Possible Melanoma",
            "causes": "Abnormal skin cell growth.",
            "suggestion": "Consult a dermatologist immediately for examination.",
            "seriousness_level": "high"
        }
    else:
        return {
            "possible_condition": "Unclear from text",
            "causes": "Description too general.",
            "suggestion": "Upload an image for better AI analysis.",
            "seriousness_level": "low"
        }
