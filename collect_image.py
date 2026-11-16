
import cv2
import os
import time

BASE_DIR = "dataset/images/train"

gestures = {
    "1": "open_hand",
    "2": "closed_fist",
    "3": "thumbs_up",
    "4": "peace",
    "5": "pointing"
}

for gesture in gestures.values():
    os.makedirs(os.path.join(BASE_DIR, gesture), exist_ok=True)

counts = {}

for gesture in gestures.values():
    folder = os.path.join(BASE_DIR, gesture)
    counts[gesture] = len([
        f for f in os.listdir(folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ])

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Camera error!")
    exit()

print("Camera ready!")
print("Press 1-5 to select gesture")
print("Press SPACE to capture")
print("Press Q to quit")

selected = None

while True:

    ret, frame = cap.read()

    if not ret:
        print("Camera frame error!")
        time.sleep(0.1)
        continue

    frame = cv2.flip(frame, 1)

    cv2.putText(frame, f"Gesture: {selected}",
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (0, 255, 0), 2)

    cv2.putText(frame, "SPACE = Capture | Q = Quit",
                (20, 80), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (255, 255, 255), 2)

    if selected:
        cv2.putText(frame, f"Saved: {counts[selected]}/100",
                    (20, 120), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 255, 255), 2)

    cv2.imshow("Bionic Hand Dataset", frame)

    key = cv2.waitKey(1) & 0xFF

    if key in [ord(str(i)) for i in range(1, 6)]:
        selected = gestures[chr(key)]
        print("Selected:", selected)

    elif key == 32:

        if selected is None:
            print("Select a gesture first!")
            continue

        if counts[selected] >= 100:
            print("100 images already collected!")
            continue

        folder = os.path.join(BASE_DIR, selected)

        filename = f"{selected}_{counts[selected]+1:04d}.jpg"

        filepath = os.path.join(folder, filename)

        success = cv2.imwrite(filepath, frame)

        if success:
            counts[selected] += 1
            print("Image saved:", filepath)
            print("Total:", counts[selected], "/100")
        else:
            print("Image could not be saved!")

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print("\nFINAL IMAGE COUNTS:")
print(counts)
print("Collection finished!")
