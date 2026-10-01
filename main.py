import cv2
import numpy as np
import time
import winsound
import os
import tensorflow as tf
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from ultralytics import YOLO

# --- NEW: SCI-FI HUD DRAWING FUNCTION ---
def draw_hud_box(img, pt1, pt2, color, thickness=2, corner_length=15):
    """Draws high-tech targeting reticle corners instead of a full rectangle."""
    x, y = pt1
    x_max, y_max = pt2

    # Top-Left corner
    cv2.line(img, (x, y), (x + corner_length, y), color, thickness)
    cv2.line(img, (x, y), (x, y + corner_length), color, thickness)
    # Top-Right corner
    cv2.line(img, (x_max, y), (x_max - corner_length, y), color, thickness)
    cv2.line(img, (x_max, y), (x_max, y + corner_length), color, thickness)
    # Bottom-Left corner
    cv2.line(img, (x, y_max), (x + corner_length, y_max), color, thickness)
    cv2.line(img, (x, y_max), (x, y_max - corner_length), color, thickness)
    # Bottom-Right corner
    cv2.line(img, (x_max, y_max), (x_max - corner_length, y_max), color, thickness)
    cv2.line(img, (x_max, y_max), (x_max, y_max - corner_length), color, thickness)

    # Optional: Draw a tiny center crosshair dot
    center_x = (x + x_max) // 2
    center_y = (y + y_max) // 2
    cv2.circle(img, (center_x, center_y), 1, color, -1)


def extract_square_eye_roi(frame, landmarks, eye_indices, w, h):
    pts = np.array([(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in eye_indices])
    x_min, y_min = np.min(pts, axis=0)
    x_max, y_max = np.max(pts, axis=0)

    box_w = x_max - x_min
    box_h = y_max - y_min
    center_x = (x_min + x_max) // 2
    center_y = (y_min + y_max) // 2

    side_length = int(max(box_w, box_h) * 1.6)
    x1 = max(0, center_x - side_length // 2)
    y1 = max(0, center_y - side_length // 2)
    x2 = min(w, center_x + side_length // 2)
    y2 = min(h, center_y + side_length // 2)

    eye_roi = frame[y1:y2, x1:x2]
    
    if eye_roi.size == 0 or eye_roi.shape[0] == 0 or eye_roi.shape[1] == 0:
        return None, None, (x1, y1, x2, y2)

    gray_eye = cv2.cvtColor(eye_roi, cv2.COLOR_BGR2GRAY)
    resized_eye = cv2.resize(gray_eye, (64, 64))
    input_tensor = np.expand_dims(resized_eye, axis=-1).astype(np.float32)

    return input_tensor, resized_eye, (x1, y1, x2, y2)

def main():
    print("Initializing DriveSafe-AI (Sci-Fi HUD Engine Activated)...")
    
    alarm_path = "alarm.wav"
    drowsiness_cnn = tf.keras.models.load_model("core/models/drowsiness_cnn.keras")
    road_model = YOLO("yolov8n.pt")

    base_options = python.BaseOptions(model_asset_path='core/models/face_landmarker.task')
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False,
        num_faces=1,
        min_face_detection_confidence=0.3,
        min_face_presence_confidence=0.3,
        min_tracking_confidence=0.3
    )
    detector = vision.FaceLandmarker.create_from_options(options)

    RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
    LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
    
    CNN_THRESHOLD = 0.85        
    DROWSY_FRAMES = 8           
    HEAD_DROP_THRESHOLD = 0.75  
    
    counter = 0
    alarm_playing = False

    driver_cam = cv2.VideoCapture(0)
    road_cam = cv2.VideoCapture(1) 
    time.sleep(1.0)

    prev_time = time.time()
    frame_count = 0
    annotated_road_frame = None

    while True:
        ret_driver, frame_driver = driver_cam.read()
        ret_road, frame_road = road_cam.read()

        if not ret_driver and not ret_road:
            break
            
        if not ret_driver:
            frame_driver = np.zeros((480, 640, 3), dtype=np.uint8)
        if not ret_road:
            frame_road = np.zeros((480, 640, 3), dtype=np.uint8)

        frame_count += 1
        
        # Create a transparent overlay layer for holographic effects
        overlay = frame_driver.copy()

        if frame_count % 3 == 0 or annotated_road_frame is None:
            road_results = road_model(frame_road, imgsz=320, conf=0.35, verbose=False)
            annotated_road_frame = road_results[0].plot()

        h, w, _ = frame_driver.shape
        rgb_driver = cv2.cvtColor(frame_driver, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_driver)
        detection_result = detector.detect(mp_image)

        drowsy_alert = False
        head_drop_alert = False
        eye_state_label = "SYS: SCANNING..." 

        if detection_result.face_landmarks:
            landmarks = detection_result.face_landmarks[0]

            nose_y = landmarks[1].y
            if nose_y > HEAD_DROP_THRESHOLD:
                head_drop_alert = True
                eye_state_label = "ERR: HEAD DROPPED"

            # 1. DRAW SCI-FI HEAD TRACKER (Cyan Color)
            head_color = (255, 255, 0) # Cyan/Jarvis Blue in BGR
            x_coords = [int(lm.x * w) for lm in landmarks]
            y_coords = [int(lm.y * h) for lm in landmarks]
            fx_min, fx_max = max(0, min(x_coords)), min(w, max(x_coords))
            fy_min, fy_max = max(0, min(y_coords)), min(h, max(y_coords))
            
            draw_hud_box(frame_driver, (fx_min, fy_min), (fx_max, fy_max), head_color, thickness=2, corner_length=30)
            
            # HUD Head Tracking Text
            cv2.putText(frame_driver, f"TGT_LCK [{fx_min},{fy_min}]", (fx_min, fy_min - 10), 
                        cv2.FONT_HERSHEY_PLAIN, 0.8, head_color, 1)

            if not head_drop_alert:
                r_tensor, r_crop, r_box = extract_square_eye_roi(frame_driver, landmarks, RIGHT_EYE_INDICES, w, h)
                l_tensor, l_crop, l_box = extract_square_eye_roi(frame_driver, landmarks, LEFT_EYE_INDICES, w, h)

                if r_tensor is not None and l_tensor is not None:
                    eye_batch = np.array([r_tensor, l_tensor])
                    predictions = drowsiness_cnn(eye_batch, training=False).numpy()
                    r_pred, l_pred = predictions[0][0], predictions[1][0]
                    avg_score = (r_pred + l_pred) / 2.0

                    # 2. DRAW HOLOGRAPHIC EYE TRACKERS
                    if avg_score > CNN_THRESHOLD:
                        box_color = (0, 255, 0) # Glowing Green
                        # Draw translucent green fill on the overlay layer
                        cv2.rectangle(overlay, (r_box[0], r_box[1]), (r_box[2], r_box[3]), (0, 255, 0), -1)
                        cv2.rectangle(overlay, (l_box[0], l_box[1]), (l_box[2], l_box[3]), (0, 255, 0), -1)
                    else:
                        box_color = (0, 0, 255) # Critical Red
                        # Draw translucent red fill on the overlay layer
                        cv2.rectangle(overlay, (r_box[0], r_box[1]), (r_box[2], r_box[3]), (0, 0, 255), -1)
                        cv2.rectangle(overlay, (l_box[0], l_box[1]), (l_box[2], l_box[3]), (0, 0, 255), -1)
                    
                    # Draw high-tech corners over the filled boxes
                    draw_hud_box(frame_driver, (r_box[0], r_box[1]), (r_box[2], r_box[3]), box_color, corner_length=8)
                    draw_hud_box(frame_driver, (l_box[0], l_box[1]), (l_box[2], l_box[3]), box_color, corner_length=8)

                    # Micro-text for eye coordinates
                    cv2.putText(frame_driver, "R_OPTIC", (r_box[0], r_box[1] - 5), cv2.FONT_HERSHEY_PLAIN, 0.7, box_color, 1)
                    cv2.putText(frame_driver, "L_OPTIC", (l_box[0], l_box[1] - 5), cv2.FONT_HERSHEY_PLAIN, 0.7, box_color, 1)

                    if avg_score <= CNN_THRESHOLD:
                        counter += 1
                        eye_state_label = f"SYS: CRITICAL ({avg_score:.2f})"
                        if counter >= DROWSY_FRAMES:
                            drowsy_alert = True
                    else:
                        counter = 0
                        eye_state_label = f"SYS: OPTIMAL ({avg_score:.2f})"

        # BLEND THE HOLOGRAPHIC OVERLAY (20% opacity for the colored boxes)
        cv2.addWeighted(overlay, 0.2, frame_driver, 0.8, 0, frame_driver)

        if drowsy_alert or head_drop_alert:
            # Flashing red border around the entire frame
            if int(time.time() * 10) % 2 == 0:
                cv2.rectangle(frame_driver, (0, 0), (w, h), (0, 0, 255), 10)
            
            if not alarm_playing:
                winsound.PlaySound(alarm_path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
                alarm_playing = True
        else:
            if alarm_playing:
                winsound.PlaySound(None, winsound.SND_PURGE)
                alarm_playing = False

        # D. MAIN DASHBOARD OVERLAYS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
        prev_time = curr_time

        state_color = (0, 255, 0) if "OPTIMAL" in eye_state_label else ((255, 255, 0) if "SCANNING" in eye_state_label else (0, 0, 255))
        
        # High-Tech Header
        cv2.putText(frame_driver, f"DRIVESAFE-AI // {eye_state_label}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, state_color, 2)
        cv2.line(frame_driver, (10, 40), (400, 40), state_color, 1) # Underline for aesthetic
        
        if drowsy_alert:
            cv2.putText(frame_driver, ">> WARNING: DRIVER SLEEPING <<", (10, 80), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
                        
        if head_drop_alert:
            cv2.putText(frame_driver, ">> WARNING: HEAD DROP DETECTED <<", (10, 120), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 3)

        frame_driver_resized = cv2.resize(frame_driver, (640, 480))
        frame_road_resized = cv2.resize(annotated_road_frame, (640, 480))

        # Bottom System Info
        cv2.putText(frame_driver_resized, "CAM_00: INTERNAL [CNN-LINKED]", (15, 460), 
                    cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), 1)
        cv2.putText(frame_road_resized, f"CAM_01: EXTERNAL [YOLO] | FPS: {int(fps)}", (15, 460), 
                    cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), 1)

        combined_view = cv2.hconcat([frame_road_resized, frame_driver_resized])
        cv2.imshow("DriveSafe - AI : Production Dashboard", combined_view)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            winsound.PlaySound(None, winsound.SND_PURGE)
            break

    driver_cam.release()
    road_cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()