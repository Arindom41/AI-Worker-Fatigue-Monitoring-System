"""
REBA scoring engine.
Combines body-part scores with the lookup tables to produce
an intermediate and final REBA score.
"""

from ergonomics.reba import score_body_parts
from ergonomics.tables import (
    lookup_table_a,
    lookup_table_b,
    lookup_table_c,
)


def calculate_reba(
    back_angle,
    neck_angle,
    knee_angle,
    left_upper,
    right_upper,
    left_lower,
    right_lower,
    trunk_twisted=False,
    trunk_side_bent=False,
    neck_twisted=False,
    neck_side_bent=False,
    shoulder_raised=False,
    arm_abducted=False,
    arm_supported=False,
    wrist_score=1,
    load_score=0,
    coupling_score=0,
    activity_score=0,
):
    """Calculate the REBA score from body angles."""

    scores = score_body_parts(
        back_angle,
        neck_angle,
        knee_angle,
        left_upper,
        right_upper,
        left_lower,
        right_lower,
        trunk_twisted=trunk_twisted,
        trunk_side_bent=trunk_side_bent,
        neck_twisted=neck_twisted,
        neck_side_bent=neck_side_bent,
        shoulder_raised=shoulder_raised,
        arm_abducted=arm_abducted,
        arm_supported=arm_supported,
    )

    score_a = lookup_table_a(
        scores["trunk"],
        scores["neck"],
        scores["legs"],
    )

    score_b = lookup_table_b(
        scores["upper_arm"],
        scores["lower_arm"],
        wrist_score,
    )

    score_b += coupling_score
    score_b = min(score_b, 12)

    final_score = lookup_table_c(score_a, score_b)

    final_score += load_score
    final_score += activity_score

    final_score = max(1, min(15, final_score))

    if final_score == 1:
        risk = "NEGLIGIBLE"
    elif final_score <= 3:
        risk = "LOW"
    elif final_score <= 7:
        risk = "MEDIUM"
    elif final_score <= 10:
        risk = "HIGH"
    else:
        risk = "VERY HIGH"

    return {
        "trunk": scores["trunk"],
        "neck": scores["neck"],
        "legs": scores["legs"],
        "upper_arm": scores["upper_arm"],
        "lower_arm": scores["lower_arm"],
        "score_a": score_a,
        "score_b": score_b,
        "reba": final_score,
        "risk": risk,
    }