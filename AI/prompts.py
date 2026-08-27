def recommendation_summary_prompt(context: dict, recommendations: list[dict]) -> str:
    return (
        'You are a helpful local travel companion. Give a concise, practical summary '
        'of these ranked recommendations. Do not invent facts, prices, or opening hours. '
        f"The user's context is: {context}. Recommendations: {recommendations}"
    )
