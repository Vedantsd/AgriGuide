WEIGHTS = {
    "ph": 2.0,
    "moisture": 1.5,
    "temperature": 1.5,
    "rainfall": 1.5,
    "nitrogen": 1.0,
    "phosphorus": 1.0,
    "potassium": 1.0,
    "soil_type": 1.5,
    "location": 1.0,
}


def range_score(value, mn, mx):
    if value is None:
        return 0.5
    mn, mx = float(mn), float(mx)
    if mn <= value <= mx:
        return 1.0
    span = (mx - mn) if mx > mn else 1.0
    dist = (mn - value) if value < mn else (value - mx)
    return max(0.0, 1.0 - dist / span)


def nutrient_score(value, target, tolerance=0.35):
    if value is None or not target:
        return 0.5
    target = float(target)
    return max(0.0, 1.0 - (abs(value - target) / target) / tolerance)


def categorical_score(user_value, crop_value, no_input_score=0.6, mismatch_score=0.4):
    if not user_value:
        return no_input_score
    same = user_value.strip().lower() == str(crop_value).strip().lower()
    return 1.0 if same else mismatch_score


def score_crop(user, crop):
    scores = {
        "ph": range_score(user["ph"], crop["ph_min"], crop["ph_max"]),
        "moisture": range_score(user["moisture"], crop["moisture_min"], crop["moisture_max"]),
        "temperature": range_score(user["temperature"], crop["temperature_min"], crop["temperature_max"]),
        "rainfall": range_score(user["rainfall"], crop["rainfall_min"], crop["rainfall_max"]),
        "nitrogen": nutrient_score(user["nitrogen"], crop["nitrogen"]),
        "phosphorus": nutrient_score(user["phosphorus"], crop["phosphorus"]),
        "potassium": nutrient_score(user["potassium"], crop["potassium"]),
        "soil_type": categorical_score(user["soil_type"], crop["soil_type"]),
        "location": categorical_score(user["location"], crop["location"], mismatch_score=0.5),
    }
    total_weight = sum(WEIGHTS.values())
    return sum(scores[k] * WEIGHTS[k] for k in scores) / total_weight


def planting_window(crop):
    start, end = crop.get("month_start"), crop.get("month_end")
    if start is None or end is None:
        return "Not specified"
    return f"Month {int(start)} \u2192 {int(end)}"


def rank_crops(user, crops):
    ranked = []
    for crop in crops:
        ranked.append({
            "crop_name": crop["crop_name"],
            "match_percent": round(score_crop(user, crop) * 100, 1),
            "soil_type": crop["soil_type"],
            "location": crop["location"],
            "ph_range": f'{crop["ph_min"]}\u2013{crop["ph_max"]}',
            "moisture_range": f'{crop["moisture_min"]}\u2013{crop["moisture_max"]}%',
            "temperature_range": f'{crop["temperature_min"]}\u2013{crop["temperature_max"]}\u00b0C',
            "rainfall_range": f'{crop["rainfall_min"]}\u2013{crop["rainfall_max"]}mm',
            "npk": f'N {crop["nitrogen"]} / P {crop["phosphorus"]} / K {crop["potassium"]}',
            "planting_window": planting_window(crop),
        })
    ranked.sort(key=lambda r: r["match_percent"], reverse=True)
    return ranked