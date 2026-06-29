"""
Activity scoring and time-persistence logic for the REBA-based worker
monitoring system.

This module adapts the REBA activity component for continuous video.
"""

import time

# Time thresholds (seconds)
STATIC_POSTURE_THRESHOLD = 60.0   # Official REBA static posture criterion
WARNING_THRESHOLD = 10.0          # Project warning
HIGH_RISK_THRESHOLD = 20.0        # Project high-risk warning
ALERT_THRESHOLD = 30.0            # Project alert
GRACE_PERIOD = 2.0                # Ignore brief tracking losses

 
# NOTE:
# The WARNING/HIGH RISK/ALERT thresholds are project-specific user notifications.
# The returned activity_score follows the REBA activity component and is kept
# independent of those notification thresholds.
def update_activity(worker, reba_score, risk_threshold=4):
    """
    Update the worker's unsafe posture timer.

    Expected worker dictionary keys:
        unsafe_start
        unsafe_duration
        status
        alert
    """

    now = time.time()

    worker.setdefault("unsafe_start", None)
    worker.setdefault("safe_start", None)
    worker.setdefault("unsafe_duration", 0.0)
    worker.setdefault("status", "SAFE")
    worker.setdefault("alert", False)

    if reba_score >= risk_threshold:
        # Unsafe posture detected again, cancel pending reset
        worker["safe_start"] = None

        if worker["unsafe_start"] is None:
            worker["unsafe_start"] = now

        worker["unsafe_duration"] = now - worker["unsafe_start"]

        duration = worker["unsafe_duration"]

        if duration >= ALERT_THRESHOLD:
            worker["status"] = "ALERT"
            worker["alert"] = True
        elif duration >= HIGH_RISK_THRESHOLD:
            worker["status"] = "HIGH RISK"
            worker["alert"] = False
        elif duration >= WARNING_THRESHOLD:
            worker["status"] = "WARNING"
            worker["alert"] = False
        else:
            worker["status"] = "MONITORING"
            worker["alert"] = False

        # Official REBA activity score adaptation.
        # A sustained static posture (>60 s) contributes +1.
        activity_score = 1 if duration >= STATIC_POSTURE_THRESHOLD else 0

    else:
        # Worker is currently in a safe posture.
        # Do not reset immediately—allow a grace period for brief tracking losses.

        if worker["safe_start"] is None:
            worker["safe_start"] = now

        safe_duration = now - worker["safe_start"]

        if safe_duration < GRACE_PERIOD:
            # Preserve the unsafe timer during short interruptions.
            activity_score = 0

            if worker["unsafe_start"] is not None:
                worker["status"] = "TRACKING"
        else:
            worker["unsafe_start"] = None
            worker["safe_start"] = None
            worker["unsafe_duration"] = 0.0
            worker["status"] = "SAFE"
            worker["alert"] = False
            activity_score = 0

    return activity_score, worker