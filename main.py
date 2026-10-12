import cv2
import numpy as np
import time
import winsound
import tensorflow as tf
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# ============================================================
# SCI-FI HUD BOX
# ============================================================

def draw_hud_box(
    img,
    pt1,
    pt2,
    color,
    thickness=2,
    corner_length=15
):
    x, y = pt1
    x_max, y_max = pt2

    # Top-left
    cv2.line(
        img,
        (x, y),
        (x + corner_length, y),
        color,
        thickness
    )

    cv2.line(
        img,
        (x, y),
        (x, y + corner_length),
        color,
        thickness
    )

    # Top-right
    cv2.line(
        img,
        (x_max, y),
        (x_max - corner_length, y),
        color,
        thickness
    )

    cv2.line(
        img,
        (x_max, y),
        (x_max, y + corner_length),
        color,
        thickness
    )

    # Bottom-left
    cv2.line(
        img,
        (x, y_max),
        (x + corner_length, y_max),
        color,
        thickness
    )

    cv2.line(
        img,
        (x, y_max),
        (x, y_max - corner_length),
        color,
        thickness
    )

    # Bottom-right
    cv2.line(
        img,
        (x_max, y_max),
        (x_max - corner_length, y_max),
        color,
        thickness
    )

    cv2.line(
        img,
        (x_max, y_max),
        (x_max, y_max - corner_length),
        color,
        thickness
    )

    # Center dot
    center_x = (x + x_max) // 2
    center_y = (y + y_max) // 2

    cv2.circle(
        img,
        (center_x, center_y),
        2,
        color,
        -1
    )


# ============================================================
# EYE ROI
# ============================================================

def extract_square_eye_roi(
    frame,
    landmarks,
    eye_indices,
    w,
    h
):

    pts = np.array([
        (
            int(landmarks[i].x * w),
            int(landmarks[i].y * h)
        )
        for i in eye_indices
    ])

    x_min, y_min = np.min(pts, axis=0)
    x_max, y_max = np.max(pts, axis=0)

    box_w = x_max - x_min
    box_h = y_max - y_min

    center_x = (x_min + x_max) // 2
    center_y = (y_min + y_max) // 2

    side_length = int(
        max(box_w, box_h) * 1.6
    )

    x1 = max(
        0,
        center_x - side_length // 2
    )

    y1 = max(
        0,
        center_y - side_length // 2
    )

    x2 = min(
        w,
        center_x + side_length // 2
    )

    y2 = min(
        h,
        center_y + side_length // 2
    )

    eye_roi = frame[y1:y2, x1:x2]

    if (
        eye_roi.size == 0
        or eye_roi.shape[0] == 0
        or eye_roi.shape[1] == 0
    ):
        return None, None, (x1, y1, x2, y2)

    gray_eye = cv2.cvtColor(
        eye_roi,
        cv2.COLOR_BGR2GRAY
    )

    resized_eye = cv2.resize(
        gray_eye,
        (64, 64)
    )

    input_tensor = np.expand_dims(
        resized_eye,
        axis=-1
    ).astype(np.float32)

    return (
        input_tensor,
        resized_eye,
        (x1, y1, x2, y2)
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "Initializing DriveSafe-AI "
        "(Sci-Fi HUD Mode)..."
    )

    # ========================================================
    # LOAD DROWSINESS MODEL
    # ========================================================

    drowsiness_cnn = tf.keras.models.load_model(
        "core/models/drowsiness_cnn.keras"
    )

    # ========================================================
    # MEDIAPIPE VISION
    # ========================================================

    base_options = python.BaseOptions(
        model_asset_path="core/models/face_landmarker.task"
    )

    options = vision.FaceLandmarkerOptions(
        base_options=base_options,

        output_face_blendshapes=False,

        output_facial_transformation_matrixes=False,

        num_faces=1,

        min_face_detection_confidence=0.3,

        min_face_presence_confidence=0.3,

        min_tracking_confidence=0.3
    )

    detector = (
        vision.FaceLandmarker
        .create_from_options(options)
    )

    # ========================================================
    # EYE LANDMARKS
    # ========================================================

    RIGHT_EYE_INDICES = [
        33,
        160,
        158,
        133,
        153,
        144
    ]

    LEFT_EYE_INDICES = [
        362,
        385,
        387,
        263,
        373,
        380
    ]

    # ========================================================
    # SETTINGS
    # ========================================================

    CNN_THRESHOLD = 0.85

    DROWSY_FRAMES = 8

    HEAD_DROP_THRESHOLD = 0.75

    counter = 0

    alarm_playing = False

    alarm_path = "alarm.wav"

    # ========================================================
    # ONLY DRIVER WEBCAM
    # ========================================================

    driver_cam = cv2.VideoCapture(0)

    driver_cam.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        1280
    )

    driver_cam.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        720
    )

    time.sleep(1)

    # ========================================================
    # MAIN LOOP
    # ========================================================

    while True:

        ret, frame = driver_cam.read()

        if not ret:

            print("Unable to read webcam.")

            break

        h, w, _ = frame.shape

        # ====================================================
        # RGB FOR MEDIAPIPE
        # ====================================================

        rgb_driver = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_driver
        )

        detection_result = detector.detect(
            mp_image
        )

        drowsy_alert = False

        head_drop_alert = False

        eye_state_label = "SCANNING..."

        # ====================================================
        # FACE DETECTED
        # ====================================================

        if detection_result.face_landmarks:

            landmarks = (
                detection_result.face_landmarks[0]
            )

            # =================================================
            # HEAD DROP
            # =================================================

            nose_y = landmarks[1].y

            if nose_y > HEAD_DROP_THRESHOLD:

                head_drop_alert = True

                eye_state_label = (
                    "HEAD DROP DETECTED"
                )

            # =================================================
            # FACE HUD
            # =================================================

            head_color = (
                255,
                255,
                0
            )

            x_coords = [
                int(lm.x * w)
                for lm in landmarks
            ]

            y_coords = [
                int(lm.y * h)
                for lm in landmarks
            ]

            fx_min = max(
                0,
                min(x_coords)
            )

            fx_max = min(
                w - 1,
                max(x_coords)
            )

            fy_min = max(
                0,
                min(y_coords)
            )

            fy_max = min(
                h - 1,
                max(y_coords)
            )

            draw_hud_box(
                frame,
                (fx_min, fy_min),
                (fx_max, fy_max),
                head_color,
                thickness=2,
                corner_length=30
            )

            # =================================================
            # FACE TARGET TEXT
            # =================================================

            cv2.putText(
                frame,
                "FACE TRACK",
                (
                    fx_min,
                    max(20, fy_min - 10)
                ),
                cv2.FONT_HERSHEY_PLAIN,
                1.0,
                head_color,
                1
            )

            # =================================================
            # EYE PROCESSING
            # =================================================

            if not head_drop_alert:

                r_tensor, r_crop, r_box = (
                    extract_square_eye_roi(
                        frame,
                        landmarks,
                        RIGHT_EYE_INDICES,
                        w,
                        h
                    )
                )

                l_tensor, l_crop, l_box = (
                    extract_square_eye_roi(
                        frame,
                        landmarks,
                        LEFT_EYE_INDICES,
                        w,
                        h
                    )
                )

                if (
                    r_tensor is not None
                    and l_tensor is not None
                ):

                    eye_batch = np.array([
                        r_tensor,
                        l_tensor
                    ])

                    # =========================================
                    # CNN
                    # =========================================

                    predictions = (
                        drowsiness_cnn(
                            eye_batch,
                            training=False
                        ).numpy()
                    )

                    r_pred = predictions[0][0]

                    l_pred = predictions[1][0]

                    avg_score = (
                        r_pred + l_pred
                    ) / 2.0

                    # =========================================
                    # EYE HUD COLOR
                    # =========================================

                    if avg_score > CNN_THRESHOLD:

                        box_color = (
                            0,
                            255,
                            0
                        )

                        eye_state_label = (
                            f"OPTIMAL  {avg_score:.2f}"
                        )

                    else:

                        box_color = (
                            0,
                            0,
                            255
                        )

                        eye_state_label = (
                            f"CRITICAL  {avg_score:.2f}"
                        )

                    # =========================================
                    # EYE HUD
                    # =========================================

                    draw_hud_box(
                        frame,
                        (
                            r_box[0],
                            r_box[1]
                        ),
                        (
                            r_box[2],
                            r_box[3]
                        ),
                        box_color,
                        thickness=2,
                        corner_length=10
                    )

                    draw_hud_box(
                        frame,
                        (
                            l_box[0],
                            l_box[1]
                        ),
                        (
                            l_box[2],
                            l_box[3]
                        ),
                        box_color,
                        thickness=2,
                        corner_length=10
                    )

                    # =========================================
                    # EYE LABELS
                    # =========================================

                    cv2.putText(
                        frame,
                        "R-OPTIC",
                        (
                            r_box[0],
                            max(
                                15,
                                r_box[1] - 7
                            )
                        ),
                        cv2.FONT_HERSHEY_PLAIN,
                        0.8,
                        box_color,
                        1
                    )

                    cv2.putText(
                        frame,
                        "L-OPTIC",
                        (
                            l_box[0],
                            max(
                                15,
                                l_box[1] - 7
                            )
                        ),
                        cv2.FONT_HERSHEY_PLAIN,
                        0.8,
                        box_color,
                        1
                    )

                    # =========================================
                    # DROWSINESS COUNTER
                    # =========================================

                    if avg_score <= CNN_THRESHOLD:

                        counter += 1

                        if counter >= DROWSY_FRAMES:

                            drowsy_alert = True

                    else:

                        counter = 0

        else:

            counter = 0

            eye_state_label = "NO FACE"

        # ====================================================
        # ALARM
        # ====================================================

        if (
            drowsy_alert
            or head_drop_alert
        ):

            if not alarm_playing:

                winsound.PlaySound(
                    alarm_path,
                    winsound.SND_FILENAME
                    | winsound.SND_ASYNC
                    | winsound.SND_LOOP
                )

                alarm_playing = True

        else:

            if alarm_playing:

                winsound.PlaySound(
                    None,
                    winsound.SND_PURGE
                )

                alarm_playing = False

        # ====================================================
        # TOP HUD STATUS
        # ====================================================

        if drowsy_alert:

            status_color = (
                0,
                0,
                255
            )

        elif head_drop_alert:

            status_color = (
                0,
                165,
                255
            )

        elif "OPTIMAL" in eye_state_label:

            status_color = (
                0,
                255,
                0
            )

        else:

            status_color = (
                255,
                255,
                0
            )

        # ====================================================
        # TOP LEFT STATUS
        # ====================================================

        cv2.putText(
            frame,
            "DRIVESAFE-AI",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            status_color,
            2
        )

        cv2.line(
            frame,
            (20, 48),
            (330, 48),
            status_color,
            1
        )

        cv2.putText(
            frame,
            f"VISION // {eye_state_label}",
            (20, 72),
            cv2.FONT_HERSHEY_PLAIN,
            1.0,
            status_color,
            1
        )

        # ====================================================
        # DANGER WARNING
        # ====================================================

        if drowsy_alert:

            # Flashing border
            if int(time.time() * 8) % 2 == 0:

                cv2.rectangle(
                    frame,
                    (5, 5),
                    (w - 6, h - 6),
                    (0, 0, 255),
                    8
                )

            # Warning
            cv2.putText(
                frame,
                "!! DROWSINESS DETECTED !!",
                (
                    20,
                    h - 55
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                3
            )

        elif head_drop_alert:

            cv2.rectangle(
                frame,
                (5, 5),
                (w - 6, h - 6),
                (0, 165, 255),
                6
            )

            cv2.putText(
                frame,
                "!! HEAD DROP DETECTED !!",
                (
                    20,
                    h - 55
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 165, 255),
                3
            )

        # ====================================================
        # WEBCAM ONLY
        # ====================================================

        cv2.imshow(
            "DriveSafe-AI",
            frame
        )

        # ====================================================
        # EXIT
        # ====================================================

        if cv2.waitKey(1) & 0xFF == ord("q"):

            break

    # ========================================================
    # CLEANUP
    # ========================================================

    if alarm_playing:

        winsound.PlaySound(
            None,
            winsound.SND_PURGE
        )

    driver_cam.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()