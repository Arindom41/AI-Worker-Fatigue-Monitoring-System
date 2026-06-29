import numpy as np


def calculate_angle(a, b, c):
    """
    Calculate angle ABC in degrees.
    b is the vertex.
    """

    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    ba = a - b
    bc = c - b

    # Prevent division by zero
    if np.linalg.norm(ba) == 0 or np.linalg.norm(bc) == 0:
        return None

    cosine = np.dot(ba, bc) / (
        np.linalg.norm(ba) * np.linalg.norm(bc)
    )

    # Numerical stability
    cosine = np.clip(cosine, -1.0, 1.0)

    angle = np.degrees(np.arccos(cosine))

    return float(angle)


def is_valid_angle(angle, min_angle, max_angle):

    if angle is None:
        return False

    if np.isnan(angle):
        return False

    if angle < min_angle:
        return False

    if angle > max_angle:
        return False

    return True


def moving_average(values, window=5):

    if len(values) == 0:
        return None

    values = values[-window:]

    return round(np.mean(values), 2)


def calculate_back_angle(person_points):
    """
    Uses:

    5  Left Shoulder
    6  Right Shoulder

    11 Left Hip
    12 Right Hip

    13 Left Knee
    14 Right Knee
    """

    try:

        left_shoulder = person_points[5]
        right_shoulder = person_points[6]

        left_hip = person_points[11]
        right_hip = person_points[12]

        left_knee = person_points[13]
        right_knee = person_points[14]

        mid_shoulder = (

            (left_shoulder[0] + right_shoulder[0]) / 2,

            (left_shoulder[1] + right_shoulder[1]) / 2

        )

        mid_hip = (

            (left_hip[0] + right_hip[0]) / 2,

            (left_hip[1] + right_hip[1]) / 2

        )

        mid_knee = (

            (left_knee[0] + right_knee[0]) / 2,

            (left_knee[1] + right_knee[1]) / 2

        )

        angle = calculate_angle(

            mid_shoulder,

            mid_hip,

            mid_knee

        )

        return angle

    except:

        return None


def calculate_neck_angle(person_points):

    try:

        nose = person_points[0]

        left_shoulder = person_points[5]
        right_shoulder = person_points[6]

        left_hip = person_points[11]
        right_hip = person_points[12]

        mid_shoulder = (

            (left_shoulder[0] + right_shoulder[0]) / 2,

            (left_shoulder[1] + right_shoulder[1]) / 2

        )

        mid_hip = (

            (left_hip[0] + right_hip[0]) / 2,

            (left_hip[1] + right_hip[1]) / 2

        )

        angle = calculate_angle(

            nose,

            mid_shoulder,

            mid_hip

        )

        return angle

    except:

        return None


def calculate_knee_angle(person_points):

    try:

        left_hip = person_points[11]

        left_knee = person_points[13]

        left_ankle = person_points[15]

        angle = calculate_angle(

            left_hip,

            left_knee,

            left_ankle

        )

        return angle

    except:

        return None


def calculate_left_upper_arm_angle(person_points):
    try:
        left_hip = person_points[11]
        left_shoulder = person_points[5]
        left_elbow = person_points[7]
        return calculate_angle(left_hip, left_shoulder, left_elbow)
    except:
        return None


def calculate_right_upper_arm_angle(person_points):
    try:
        right_hip = person_points[12]
        right_shoulder = person_points[6]
        right_elbow = person_points[8]
        return calculate_angle(right_hip, right_shoulder, right_elbow)
    except:
        return None


def calculate_left_lower_arm_angle(person_points):
    try:
        left_shoulder = person_points[5]
        left_elbow = person_points[7]
        left_wrist = person_points[9]
        return calculate_angle(left_shoulder, left_elbow, left_wrist)
    except:
        return None


def calculate_right_lower_arm_angle(person_points):
    try:
        right_shoulder = person_points[6]
        right_elbow = person_points[8]
        right_wrist = person_points[10]
        return calculate_angle(right_shoulder, right_elbow, right_wrist)
    except:
        return None


def calculate_left_leg_angle(person_points):
    try:
        left_hip = person_points[11]
        left_knee = person_points[13]
        left_ankle = person_points[15]
        return calculate_angle(left_hip, left_knee, left_ankle)
    except:
        return None


def calculate_right_leg_angle(person_points):
    try:
        right_hip = person_points[12]
        right_knee = person_points[14]
        right_ankle = person_points[16]
        return calculate_angle(right_hip, right_knee, right_ankle)
    except:
        return None