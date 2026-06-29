"""
Official REBA body-part scoring (Phase 1).
This file converts body angles into REBA body scores.
Table A/B/C lookups will be added in the next phase.
"""


def score_trunk(back_angle, twisted=False, side_bent=False):
    if back_angle is None:
        return 0

    if back_angle < 5:
        score = 1
    elif back_angle < 20:
        score = 2
    elif back_angle < 60:
        score = 3
    else:
        score = 4

    if twisted:
        score += 1
    if side_bent:
        score += 1

    return min(score, 5)



def score_neck(neck_angle, twisted=False, side_bent=False):
    if neck_angle is None:
        return 0

    neck_flexion = abs(180 - neck_angle)

    if neck_flexion < 10:
        score = 1
    elif neck_flexion < 20:
        score = 2
    else:
        score = 3

    if twisted:
        score += 1
    if side_bent:
        score += 1

    return min(score, 3)



def score_legs(knee_angle):
    if knee_angle is None:
        return 0

    knee_flexion = abs(180 - knee_angle)

    if knee_flexion < 30:
        return 1
    elif knee_flexion < 60:
        return 2
    else:
        return 3



def score_upper_arm(left_angle,
                    right_angle,
                    shoulder_raised=False,
                    abducted=False,
                    arm_supported=False):

    angles = [a for a in (left_angle, right_angle) if a is not None]

    if not angles:
        return 0

    angle = max(angles)

    if angle < 20:
        score = 1
    elif angle < 45:
        score = 2
    elif angle < 90:
        score = 3
    else:
        score = 4

    if shoulder_raised:
        score += 1
    if abducted:
        score += 1
    if arm_supported:
        score -= 1

    score = max(1, score)
    return min(score, 6)



def score_lower_arm(left_angle, right_angle):
    angles = [a for a in (left_angle, right_angle) if a is not None]

    if not angles:
        return 0

    elbow = min(angles)

    if 60 <= elbow <= 100:
        return 1
    return 2



def score_body_parts(back_angle,
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
                     arm_supported=False):
    """Return all individual REBA body-part scores."""

    return {
        "trunk": score_trunk(
            back_angle,
            twisted=trunk_twisted,
            side_bent=trunk_side_bent,
        ),
        "neck": score_neck(
            neck_angle,
            twisted=neck_twisted,
            side_bent=neck_side_bent,
        ),
        "legs": score_legs(knee_angle),
        "upper_arm": score_upper_arm(
            left_upper,
            right_upper,
            shoulder_raised=shoulder_raised,
            abducted=arm_abducted,
            arm_supported=arm_supported,
        ),
        "lower_arm": score_lower_arm(left_lower, right_lower),
    }