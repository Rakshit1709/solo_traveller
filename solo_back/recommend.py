# recommend.py (functions)
import math

def parse_tags(tags_str):
    return [t.strip().lower() for t in tags_str.split(",") if t.strip()]

def tag_match_score(user_hobbies, place_tags):
    # count of matching tags
    matches = len(set([h.lower() for h in user_hobbies]) & set(place_tags))
    return matches * 3  # weight each match

def rating_score(rating):
    # normalize rating 0-5 to a small boost
    return max(0, (rating - 3)) * 1.5

def budget_score(total_cost, user_budget):
    # higher score if under budget
    if user_budget is None:
        return 0
    if total_cost <= user_budget:
        return 2
    # partial credit if close
    ratio = user_budget / total_cost
    return max(0, ratio)  # 0..1

def airport_score(airport_within_50km):
    return 1.0 if airport_within_50km else 0

def compute_score(place, user_hobbies, user_budget):
    p_tags = parse_tags(place['tags'])
    s = 0
    s += tag_match_score(user_hobbies, p_tags)
    s += rating_score(place.get('google_rating', 0))
    # estimate total cost (simple): entrance + 2*stay_cost_per_day? if not available use entrance only
    total_cost_est = place.get('entrance_fee_inr',0)
    s += budget_score(total_cost_est, user_budget) * 2
    s += airport_score(place.get('airport_within_50km', False))
    # add small boost for reviews
    s += (place.get('reviews_lakhs', 0) * 0.5)
    return s
