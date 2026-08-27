from .place_service import Place, distance_km, serialize_place


DEFAULT_WEIGHTS = {
    'interest': 0.35,
    'distance': 0.20,
    'budget': 0.20,
    'time': 0.15,
    'availability': 0.10,
}


def rank_recommendations(places: list[Place], latitude: float, longitude: float,
                         interests: list[str], budget: int, available_time_minutes: int,
                         category: str = '', limit: int = 5,
                         weights: dict[str, float] | None = None) -> list[dict]:
    weights = weights or DEFAULT_WEIGHTS
    selected_interests = set(interests or [])
    if category:
        selected_interests.add(category)

    ranked = []
    for place in places:
        distance = distance_km(latitude, longitude, place.latitude, place.longitude)
        if place.estimated_cost > budget or place.visit_duration_minutes > available_time_minutes:
            continue

        interest_score = 1 if place.category in selected_interests else (0.5 if not selected_interests else 0)
        distance_score = max(0, 1 - (distance / 15))
        budget_score = max(0, 1 - (place.estimated_cost / max(budget, 1)))
        time_score = max(0, 1 - (place.visit_duration_minutes / max(available_time_minutes, 1)))
        availability_score = 1
        score = sum((value * weights[key]) for key, value in {
            'interest': interest_score,
            'distance': distance_score,
            'budget': budget_score,
            'time': time_score,
            'availability': availability_score,
        }.items())

        result = serialize_place(place, latitude, longitude)
        result['recommendation_score'] = round(score * 100, 1)
        result['reason'] = build_reason(place, distance, interest_score, budget, available_time_minutes)
        ranked.append(result)

    return sorted(ranked, key=lambda recommendation: recommendation['recommendation_score'], reverse=True)[:limit]


def build_reason(place: Place, distance: float, interest_score: float,
                 budget: int, available_time_minutes: int) -> str:
    reasons = []
    if interest_score == 1:
        reasons.append(f'it matches your interest in {place.category}')
    elif interest_score == 0.5:
        reasons.append('it is a good nearby option')
    if place.estimated_cost <= budget:
        reasons.append('it fits your budget')
    if place.visit_duration_minutes <= available_time_minutes:
        reasons.append(f'it is about {round(distance, 1)} km away')
    return 'Recommended because ' + ', '.join(reasons) + '.'
