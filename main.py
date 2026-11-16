
import cv2
import mediapipe as mp
import math

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# CALIBRATION
# Example: If a 5 cm reference object measures 100 pixels
REFERENCE_SIZE_CM = 5.0
REFERENCE_SIZE_PIXELS = 100.0

PIXELS_PER_CM = REFERENCE_SIZE_PIXELS / REFERENCE_SIZE_CM

colors = [
    (0, 255, 255),
    (255, 0, 0),
    (0, 255, 0),
    (255, 255, 0),
    (255, 0, 255),
    (0, 165, 255)
]

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
) as hands:

    while cap.isOpened():

        success, frame = cap.read()

        if not success:
            print("Camera error")
            break

        frame = cv2.flip(frame, 1)

        h, w, _ = frame.shape

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:

            for hand in results.multi_hand_landmarks:

                points = []

                for i, lm in enumerate(hand.landmark):
                    x = int(lm.x * w)
                    y = int(lm.y * h)
                    points.append((x, y))

                # Draw connections and calculate distances
                for start, end in mp_hands.HAND_CONNECTIONS:

                    x1, y1 = points[start]
                    x2, y2 = points[end]

                    cv2.line(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (255, 255, 255),
                        2
                    )

                    distance_pixels = math.hypot(
                        x2 - x1,
                        y2 - y1
                    )

                    distance_cm = distance_pixels / PIXELS_PER_CM

                    mx = (x1 + x2) // 2
                    my = (y1 + y2) // 2

                    cv2.putText(
                        frame,
                        f"{distance_cm:.1f}cm",
                        (mx, my),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (0, 0, 0),
                        3
                    )

                    cv2.putText(
                        frame,
                        f"{distance_cm:.1f}cm",
                        (mx, my),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (255, 255, 255),
                        1
                    )

                # Draw colorful landmarks
                for i, (x, y) in enumerate(points):

                    if i == 0:
                        color = colors[0]
                    elif i <= 4:
                        color = colors[1]
                    elif i <= 8:
                        color = colors[2]
                    elif i <= 12:
                        color = colors[3]
                    elif i <= 16:
                        color = colors[4]
                    else:
                        color = colors[5]

                    cv2.circle(frame, (x, y), 9, color, -1)
                    cv2.circle(frame, (x, y), 11, (255, 255, 255), 2)

                    cv2.putText(
                        frame,
                        str(i),
                        (x + 10, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 255),
                        2
                    )

                # Palm width
                palm_width_pixels = math.hypot(
                    points[5][0] - points[17][0],
                    points[5][1] - points[17][1]
                )

                palm_width_cm = palm_width_pixels / PIXELS_PER_CM

                # Near / far estimation
                if palm_width_pixels > 160:
                    status = "HAND NEAR"
                    status_color = (0, 255, 0)

                elif palm_width_pixels < 100:
                    status = "HAND FAR"
                    status_color = (0, 0, 255)

                else:
                    status = "MEDIUM DISTANCE"
                    status_color = (0, 255, 255)

                cv2.rectangle(
                    frame,
                    (10, 10),
                    (500, 135),
                    (0, 0, 0),
                    -1
                )

                cv2.putText(
                    frame,
                    "HAND DETECTED",
                    (20, 45),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    f"Palm Width: {palm_width_cm:.2f} cm",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    status,
                    (20, 115),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    status_color,
                    2
                )

        else:

            cv2.putText(
                frame,
                "NO HAND DETECTED",
                (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )

        cv2.imshow("Bionic Hand - Distance in CM", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
