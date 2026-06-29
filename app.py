from flask import Flask, render_template, request, Response, jsonify
import os

from detection.detect import (
    generate_frames,
    request_stream_stop,
    reset_stream_stop,
    workers,
)

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

video_path = None


def json_number(value, default=None):

    if value is None:
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@app.route('/')
def home():

    return render_template("index.html")


@app.route('/upload', methods=['POST'])
def upload():

    global video_path

    file = request.files['video']

    if file:

        reset_stream_stop()

        video_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            file.filename
        )

        file.save(video_path)

        return render_template(
            "index.html",
            uploaded=True
        )

    return "No file uploaded"


@app.route('/video_feed')
def video_feed():

    global video_path

    return Response(
        generate_frames(video_path),

        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/live')
def live():
    reset_stream_stop()

    return render_template('live.html')


@app.route('/video_feed_live')
def video_feed_live():
    return Response(
        generate_frames(0),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/stop_stream', methods=['POST'])
def stop_stream():

    request_stream_stop()

    return jsonify({
        "status": "stopped",
    })


@app.route('/worker_status')
def worker_status():

    worker_data = []

    for worker_id, worker in list(workers.items()):

        worker_data.append({
            "id": worker_id,
            "back": json_number(worker.get("back_angle")),
            "neck": json_number(worker.get("neck_angle")),
            "knee": json_number(worker.get("knee_angle")),
            "lua": json_number(worker.get("left_upper_arm_angle")),
            "rua": json_number(worker.get("right_upper_arm_angle")),
            "lla": json_number(worker.get("left_lower_arm_angle")),
            "rla": json_number(worker.get("right_lower_arm_angle")),
            "reba": int(json_number(worker.get("reba"), 0)),
            "risk": worker.get("risk", "SAFE"),
            "status": worker.get("status", "SAFE"),
            "unsafe_time": json_number(worker.get("unsafe_duration"), 0.0),
            "accuracy": json_number(worker.get("accuracy"), 0.0),
        })

    return jsonify(worker_data)


@app.route('/clear_workers', methods=['POST'])
def clear_workers():

    workers.clear()

    return jsonify({
        "status": "cleared",
        "workers": 0,
    })


if __name__ == "__main__":

    app.run(debug=True)
