import cv2
import time
import threading
from ergonomics.scoring import calculate_reba
from ergonomics.activity import update_activity
from ultralytics import YOLO
from utils.angles import (
    calculate_back_angle,
    calculate_neck_angle,
    calculate_knee_angle,
    calculate_left_upper_arm_angle,
    calculate_right_upper_arm_angle,
    calculate_left_lower_arm_angle,
    calculate_right_lower_arm_angle,
    calculate_left_leg_angle,
    calculate_right_leg_angle,
    is_valid_angle,
    moving_average,
)

# Single model for Detection + Pose
pose_model = YOLO("yolov8s-pose.pt")

# Store worker history
workers = {}

# Shared signal used by the Flask routes to stop the active MJPEG generator.
stream_stop_event = threading.Event()


def request_stream_stop():
    stream_stop_event.set()


def reset_stream_stop():
    stream_stop_event.clear()


def get_risk_color(risk, status="SAFE"):
    risk_key = (risk or "").upper()
    status_key = (status or "").upper()

    if status_key == "ALERT" or risk_key in ("ALERT", "VERY HIGH"):
        return (0, 0, 255)

    if risk_key == "HIGH":
        return (0, 165, 255)

    if risk_key == "MEDIUM":
        return (0, 255, 255)

    if risk_key == "LOW":
        return (144, 238, 144)

    return (0, 255, 0)


def generate_frames(video_path):

    # Accept either a webcam index (e.g. 0) or a video path
    if isinstance(video_path, int):
        cap = cv2.VideoCapture(video_path)
    else:
        cap = cv2.VideoCapture(str(video_path))

    # Configure webcam for smoother live streaming
    if isinstance(video_path, int):
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():

        print("Cannot open video")

        return

    prev = time.time()

    while not stream_stop_event.is_set():

        ret, frame = cap.read()

        if not ret:

            break

        ##################################################

        # Resize for speed and quality balance

        ##################################################

        frame = cv2.resize(

            frame,

            (1280, 720)

        )

        ##################################################

        # YOLO Pose + ByteTrack

        ##################################################

        results = pose_model.track(

            frame,

            persist=True,

            tracker="bytetrack.yaml",

            imgsz=640,

            conf=0.4,

            verbose=False

        )

        for r in results:

            if r.boxes is None:

                continue

            boxes = r.boxes

            keypoints = r.keypoints

            for i, box in enumerate(boxes):

                cls = int(box.cls[0])

                # Person class only

                if cls != 0:

                    continue

                ##################################################

                # Bounding Box

                ##################################################

                x1, y1, x2, y2 = map(

                    int,

                    box.xyxy[0]

                )

                conf = float(box.conf[0])

                ##################################################

                # Tracking ID

                ##################################################

                if box.id is not None:

                    worker_id = int(

                        box.id[0]

                    )

                else:

                    worker_id = -1

                ##################################################

                # Worker State

                ##################################################

                if worker_id not in workers:

                    workers[worker_id] = {
                        # -----------------------------
                        # Pose
                        # -----------------------------
                        "keypoints": None,

                        # -----------------------------
                        # Angle history (moving average)
                        # -----------------------------
                        "back_angles": [],
                        "neck_angles": [],
                        "knee_angles": [],
                        "left_upper_arm_angles": [],
                        "right_upper_arm_angles": [],
                        "left_lower_arm_angles": [],
                        "right_lower_arm_angles": [],
                        "left_leg_angles": [],
                        "right_leg_angles": [],

                        # -----------------------------
                        # Smoothed angles
                        # -----------------------------
                        "back_angle": None,
                        "neck_angle": None,
                        "knee_angle": None,
                        "left_upper_arm_angle": None,
                        "right_upper_arm_angle": None,
                        "left_lower_arm_angle": None,
                        "right_lower_arm_angle": None,
                        "left_leg_angle": None,
                        "right_leg_angle": None,

                        # -----------------------------
                        # REBA
                        # -----------------------------
                        "trunk_score": 0,
                        "neck_score": 0,
                        "leg_score": 0,
                        "upper_arm_score": 0,
                        "lower_arm_score": 0,

                        "score_a": 0,
                        "score_b": 0,

                        "reba": 0,
                        "risk": "SAFE",
                        "accuracy": 0.0,

                        # -----------------------------
                        # Activity / Alerts
                        # -----------------------------
                        "unsafe_start": None,
                        "safe_start": None,
                        "unsafe_duration": 0.0,

                        "status": "SAFE",
                        "alert": False,
                    }

                workers[worker_id]["accuracy"] = conf * 100

                ##################################################

                # Draw Bounding Box

                ##################################################

                box_color = get_risk_color(
                    workers[worker_id]["risk"],
                    workers[worker_id]["status"],
                )

                cv2.rectangle(

                    frame,

                    (x1, y1),

                    (x2, y2),

                    box_color,

                    2

                )

                ##################################################

                # Draw ID

                ##################################################

                label = f"ID {worker_id}"

                cv2.putText(

                    frame,

                    label,

                    (x1, y1 - 10),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.8,

                    box_color,

                    2

                )
                

                ##################################################

                # Keypoints

                ##################################################

                if keypoints is not None:

                    pts = (

                        keypoints

                        .xy

                        .cpu()

                        .numpy()

                    )

                    if len(pts) > i:

                        person_points = pts[i]

                        workers[worker_id][

                            "keypoints"

                        ] = person_points

                        back_angle = calculate_back_angle(person_points)
                        neck_angle = calculate_neck_angle(person_points)
                        knee_angle = calculate_knee_angle(person_points)

                        left_upper = calculate_left_upper_arm_angle(person_points)
                        right_upper = calculate_right_upper_arm_angle(person_points)
                        left_lower = calculate_left_lower_arm_angle(person_points)
                        right_lower = calculate_right_lower_arm_angle(person_points)
                        left_leg = calculate_left_leg_angle(person_points)
                        right_leg = calculate_right_leg_angle(person_points)

                        if is_valid_angle(back_angle, 50, 180):
                            workers[worker_id]["back_angles"].append(back_angle)
                            workers[worker_id]["back_angles"] = workers[worker_id]["back_angles"][-5:]
                            workers[worker_id]["back_angle"] = moving_average(workers[worker_id]["back_angles"])

                        if is_valid_angle(neck_angle, 80, 180):
                            workers[worker_id]["neck_angles"].append(neck_angle)
                            workers[worker_id]["neck_angles"] = workers[worker_id]["neck_angles"][-5:]
                            workers[worker_id]["neck_angle"] = moving_average(workers[worker_id]["neck_angles"])

                        if is_valid_angle(knee_angle, 60, 180):
                            workers[worker_id]["knee_angles"].append(knee_angle)
                            workers[worker_id]["knee_angles"] = workers[worker_id]["knee_angles"][-5:]
                            workers[worker_id]["knee_angle"] = moving_average(workers[worker_id]["knee_angles"])

                        if is_valid_angle(left_upper, 30, 180):
                            workers[worker_id]["left_upper_arm_angles"].append(left_upper)
                            workers[worker_id]["left_upper_arm_angles"] = workers[worker_id]["left_upper_arm_angles"][-5:]
                            workers[worker_id]["left_upper_arm_angle"] = moving_average(workers[worker_id]["left_upper_arm_angles"])

                        if is_valid_angle(right_upper, 30, 180):
                            workers[worker_id]["right_upper_arm_angles"].append(right_upper)
                            workers[worker_id]["right_upper_arm_angles"] = workers[worker_id]["right_upper_arm_angles"][-5:]
                            workers[worker_id]["right_upper_arm_angle"] = moving_average(workers[worker_id]["right_upper_arm_angles"])

                        if is_valid_angle(left_lower, 30, 180):
                            workers[worker_id]["left_lower_arm_angles"].append(left_lower)
                            workers[worker_id]["left_lower_arm_angles"] = workers[worker_id]["left_lower_arm_angles"][-5:]
                            workers[worker_id]["left_lower_arm_angle"] = moving_average(workers[worker_id]["left_lower_arm_angles"])

                        if is_valid_angle(right_lower, 30, 180):
                            workers[worker_id]["right_lower_arm_angles"].append(right_lower)
                            workers[worker_id]["right_lower_arm_angles"] = workers[worker_id]["right_lower_arm_angles"][-5:]
                            workers[worker_id]["right_lower_arm_angle"] = moving_average(workers[worker_id]["right_lower_arm_angles"])

                        if is_valid_angle(left_leg, 30, 180):
                            workers[worker_id]["left_leg_angles"].append(left_leg)
                            workers[worker_id]["left_leg_angles"] = workers[worker_id]["left_leg_angles"][-5:]
                            workers[worker_id]["left_leg_angle"] = moving_average(workers[worker_id]["left_leg_angles"])

                        if is_valid_angle(right_leg, 30, 180):
                            workers[worker_id]["right_leg_angles"].append(right_leg)
                            workers[worker_id]["right_leg_angles"] = workers[worker_id]["right_leg_angles"][-5:]
                            workers[worker_id]["right_leg_angle"] = moving_average(workers[worker_id]["right_leg_angles"])


                        ##################################################
                        # REBA CALCULATION
                        ##################################################

                        # Only calculate if all required angles are available
                        required_angles = [
                            workers[worker_id]["back_angle"],
                            workers[worker_id]["neck_angle"],
                            workers[worker_id]["knee_angle"],
                            workers[worker_id]["left_upper_arm_angle"],
                            workers[worker_id]["right_upper_arm_angle"],
                            workers[worker_id]["left_lower_arm_angle"],
                            workers[worker_id]["right_lower_arm_angle"],
                        ]

                        if all(angle is not None for angle in required_angles):

                            try:    
                                # Base REBA
                                reba_result = calculate_reba(
                                    workers[worker_id]["back_angle"],
                                    workers[worker_id]["neck_angle"],
                                    workers[worker_id]["knee_angle"],
                                    workers[worker_id]["left_upper_arm_angle"],
                                    workers[worker_id]["right_upper_arm_angle"],
                                    workers[worker_id]["left_lower_arm_angle"],
                                    workers[worker_id]["right_lower_arm_angle"],
                                )

                                # Update activity timer
                                activity_score, workers[worker_id] = update_activity(
                                    workers[worker_id],
                                    reba_result["reba"],
                                )

                                # Final REBA with activity score
                                reba_result = calculate_reba(
                                    workers[worker_id]["back_angle"],
                                    workers[worker_id]["neck_angle"],
                                    workers[worker_id]["knee_angle"],
                                    workers[worker_id]["left_upper_arm_angle"],
                                    workers[worker_id]["right_upper_arm_angle"],
                                    workers[worker_id]["left_lower_arm_angle"],
                                    workers[worker_id]["right_lower_arm_angle"],
                                    activity_score=activity_score,
                                )

                                workers[worker_id]["trunk_score"] = reba_result["trunk"]
                                workers[worker_id]["neck_score"] = reba_result["neck"]
                                workers[worker_id]["leg_score"] = reba_result["legs"]
                                workers[worker_id]["upper_arm_score"] = reba_result["upper_arm"]
                                workers[worker_id]["lower_arm_score"] = reba_result["lower_arm"]

                                workers[worker_id]["score_a"] = reba_result["score_a"]
                                workers[worker_id]["score_b"] = reba_result["score_b"]

                                workers[worker_id]["reba"] = reba_result["reba"]
                                workers[worker_id]["risk"] = reba_result["risk"]

                            except Exception as e:
                                print(f"[REBA ERROR] Worker {worker_id}: {e}")


                        if workers[worker_id]["reba"] > 0:

                            box_color = get_risk_color(
                                workers[worker_id]["risk"],
                                workers[worker_id]["status"],
                            )

                            cv2.rectangle(
                                frame,
                                (x1, y1),
                                (x2, y2),
                                box_color,
                                2,
                            )

                            cv2.putText(
                                frame,
                                label,
                                (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.8,
                                box_color,
                                2,
                            )

                            cv2.putText(
                                frame,
                                f"REBA: {workers[worker_id]['reba']}",
                                (x1, y2 + 25),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.55,
                                box_color,
                                2,
                            )

                            cv2.putText(
                                frame,
                                f"Risk: {workers[worker_id]['risk']}",
                                (x1, y2 + 48),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.55,
                                box_color,
                                2,
                            )


                        ##################################################

                        # Draw important keypoints only

                        ##################################################

                        important = [

                            0,      # Nose

                            5, 6,   # Shoulders

                            11, 12, # Hips

                            13, 14, # Knees

                            15, 16  # Ankles

                        ]

                        for idx in important:

                            px = int(

                                person_points[idx][0]

                            )

                            py = int(

                                person_points[idx][1]

                            )

                            if px == 0 and py == 0:

                                continue

                            cv2.circle(

                                frame,

                                (px, py),

                                5,

                                (0, 0, 255),

                                -1

                            )

        ##################################################

        # FPS Counter

        ##################################################

        curr = time.time()

        fps = 1 / (curr - prev)

        prev = curr

        cv2.putText(

            frame,

            f"FPS : {int(fps)}",

            (20, 40),

            cv2.FONT_HERSHEY_SIMPLEX,

            1,

            (255, 0, 0),

            2

        )

        ##################################################

        # Stream Frame

        ##################################################

        ret, buffer = cv2.imencode(

            ".jpg",

            frame

        )

        frame = buffer.tobytes()

        yield (

            b'--frame\r\n'

            b'Content-Type: image/jpeg\r\n\r\n'

            + frame +

            b'\r\n'

        )

    cap.release()












# import cv2
# from ultralytics import YOLO

# # Detection model
# det_model = YOLO("yolov8x.pt")

# # Pose model
# pose_model = YOLO("yolov8m-pose.pt")

# # Store worker history
# workers = {}


# def generate_frames(video_path):

#     cap = cv2.VideoCapture(video_path)

#     if not cap.isOpened():

#         print("Cannot open video")

#         return

#     while True:

#         ret, frame = cap.read()

#         if not ret:

#             break

#         ##################################################

#         # DETECTION + TRACKING

#         ##################################################

#         results = det_model.track(

#             frame,

#             persist=True,

#             tracker="bytetrack.yaml",

#             verbose=False

#         )

#         for r in results:

#             if r.boxes is None:

#                 continue

#             for box in r.boxes:

#                 cls = int(box.cls[0])

#                 if cls != 0:

#                     continue

#                 x1, y1, x2, y2 = map(

#                     int,

#                     box.xyxy[0]

#                 )

#                 if box.id is not None:

#                     worker_id = int(

#                         box.id[0]

#                     )

#                 else:

#                     worker_id = -1

#                 ##################################################

#                 # CROP PERSON

#                 ##################################################

#                 person = frame[y1:y2, x1:x2]

#                 if person.size == 0:

#                     continue

#                 ##################################################

#                 # POSE ESTIMATION

#                 ##################################################

#                 pose_results = pose_model(

#                     person,

#                     verbose=False

#                 )

#                 ##################################################

#                 # DRAW BOX

#                 ##################################################

#                 cv2.rectangle(

#                     frame,

#                     (x1, y1),

#                     (x2, y2),

#                     (0,255,0),

#                     2

#                 )

#                 cv2.putText(

#                     frame,

#                     f"ID {worker_id}",

#                     (x1, y1-10),

#                     cv2.FONT_HERSHEY_SIMPLEX,

#                     0.7,

#                     (0,255,0),

#                     2

#                 )

#                 ##################################################

#                 # KEYPOINTS

#                 ##################################################

#                 if (

#                     pose_results[0].keypoints

#                     is not None

#                 ):

#                     kps = (

#                         pose_results[0]

#                         .keypoints

#                         .xy

#                         .cpu()

#                         .numpy()

#                     )

#                     if len(kps)>0:

#                         points = kps[0]

#                         workers[worker_id] = {

#                             "keypoints":

#                             points

#                         }

#                         ##################################################

#                         # DRAW KEYPOINTS

#                         ##################################################

#                         for p in points:

#                             px = int(

#                                 p[0]

#                             )

#                             py = int(

#                                 p[1]

#                             )

#                             cv2.circle(

#                                 frame,

#                                 (

#                                     x1+px,

#                                     y1+py

#                                 ),

#                                 4,

#                                 (0,0,255),

#                                 -1

#                             )

#         ##################################################

#         # STREAM FRAME

#         ##################################################

#         ret, buffer = cv2.imencode(

#             ".jpg",

#             frame

#         )

#         frame = buffer.tobytes()

#         yield (

#             b'--frame\r\n'

#             b'Content-Type: image/jpeg\r\n\r\n'

#             + frame +

#             b'\r\n'

#         )

#     cap.release()



# # REBA < 4

# # → SAFE

# # ----------------

# # REBA 4 - 7

# # → WARNING

# # Unsafe posture for > 15 sec

# # ----------------

# # REBA >= 8

# # → ALERT

# # Unsafe posture for > 30 sec
