def calculate_impact_level(impact_dict):
    if 'Serious' in impact_dict.values():
        return 'Serious'
    moderate_count = sum(1 for val in impact_dict.values() if val == 'Moderate')
    if moderate_count >= 2 or impact_dict.get('financial') == 'Moderate' or impact_dict.get('operational') == 'Moderate':
        return 'Moderate'
    return 'Negligible'

def calculate_risk_level(impact, likelihood):
    impact_levels = {"Negligible": 1, "Moderate": 2, "Serious": 3}
    if impact not in impact_levels or likelihood not in range(1, 6):
        return "Invalid"

    severity_matrix = {
        3: ["High", "High", "High", "Moderate", "Low"],
        2: ["High", "Moderate", "Moderate", "Low", "Low"],
        1: ["Low"] * 5
    }
    return severity_matrix[impact_levels[impact]][likelihood - 1]