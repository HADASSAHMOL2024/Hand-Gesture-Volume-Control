import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math
import numpy as np

from pycaw.pycaw import AudioUtilities


# ============================================================
# WINDOWS AUDIO SETUP
# ============================================================

devices = AudioUtilities.GetSpeakers()
volume_control = devices.EndpointVolume


# ============================================================
# MEDIAPIPE SETUP
# ============================================================

MODEL_PATH = "hand_landmarker.task"

base_options = python.BaseOptions(
    model_asset_path=MODEL_PATH
)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.7,
    min_tracking_confidence=0.7
)

detector = vision.HandLandmarker.create_from_options(options)


# ============================================================
# WEBCAM
# ============================================================

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("❌ Could not open webcam.")
    exit()

print("==============================================")
print("       HAND GESTURE VOLUME CONTROL")
print("==============================================")
print("🤏 Thumb + Index  → Volume")
print("✊ Closed Fist    → Mute")
print("🖐️ Open Palm      → Unmute")
print("⌨️ Press Q to quit")
print("==============================================")


# ============================================================
# SETTINGS
# ============================================================

MIN_DISTANCE = 20
MAX_DISTANCE = 220

SMOOTHING_FACTOR = 0.15

# Number of consecutive frames required
# before recognizing fist/palm
GESTURE_CONFIRM_FRAMES = 10


# ============================================================
# INITIAL VOLUME
# ============================================================

smoothed_volume = (
    volume_control.GetMasterVolumeLevelScalar() * 100
)


# ============================================================
# GESTURE STATE
# ============================================================

detected_gesture = "NONE"

gesture_counter = 0

last_confirmed_gesture = "NONE"

is_muted = False


# ============================================================
# TIMESTAMP
# ============================================================

frame_timestamp = 0


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def distance_between(point1, point2):
    """
    Calculate Euclidean distance between two landmarks.
    """

    return math.sqrt(
        (point1.x - point2.x) ** 2 +
        (point1.y - point2.y) ** 2
    )


def finger_is_extended(landmarks, tip_id, pip_id):
    """
    Determine whether a finger is extended.

    The fingertip should be farther from the wrist
    than the PIP joint.
    """

    wrist = landmarks[0]

    tip_distance = distance_between(
        landmarks[tip_id],
        wrist
    )

    pip_distance = distance_between(
        landmarks[pip_id],
        wrist
    )

    return tip_distance > pip_distance


def detect_gesture(landmarks):
    """
    Detect the main hand gestures.

    Returns:
        OPEN_PALM
        CLOSED_FIST
        VOLUME
    """

    # --------------------------------------------------------
    # Check four main fingers
    # --------------------------------------------------------

    index_extended = finger_is_extended(
        landmarks, 8, 6
    )

    middle_extended = finger_is_extended(
        landmarks, 12, 10
    )

    ring_extended = finger_is_extended(
        landmarks, 16, 14
    )

    pinky_extended = finger_is_extended(
        landmarks, 20, 18
    )


    extended_count = sum([
        index_extended,
        middle_extended,
        ring_extended,
        pinky_extended
    ])


    # --------------------------------------------------------
    # OPEN PALM
    # --------------------------------------------------------

    if extended_count >= 4:
        return "OPEN_PALM"


    # --------------------------------------------------------
    # CLOSED FIST
    # --------------------------------------------------------

    if extended_count == 0:
        return "CLOSED_FIST"


    # --------------------------------------------------------
    # Otherwise volume gesture
    # --------------------------------------------------------

    return "VOLUME"


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    success, frame = cap.read()

    if not success:
        print("❌ Failed to read webcam frame.")
        break


    # --------------------------------------------------------
    # Mirror webcam
    # --------------------------------------------------------

    frame = cv2.flip(frame, 1)

    h, w, _ = frame.shape


    # --------------------------------------------------------
    # Convert BGR → RGB
    # --------------------------------------------------------

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )


    # --------------------------------------------------------
    # MediaPipe detection
    # --------------------------------------------------------

    frame_timestamp += 1

    results = detector.detect_for_video(
        mp_image,
        frame_timestamp
    )


    # ========================================================
    # HAND DETECTED
    # ========================================================

    if results.hand_landmarks:

        hand_landmarks = results.hand_landmarks[0]


        # ====================================================
        # DETECT CURRENT GESTURE
        # ====================================================

        gesture = detect_gesture(
            hand_landmarks
        )


        # ----------------------------------------------------
        # Gesture confirmation system
        # ----------------------------------------------------

        if gesture == detected_gesture:

            gesture_counter += 1

        else:

            detected_gesture = gesture
            gesture_counter = 1


        # ----------------------------------------------------
        # Confirm gesture after required frames
        # ----------------------------------------------------

        if gesture_counter >= GESTURE_CONFIRM_FRAMES:

            confirmed_gesture = detected_gesture

        else:

            confirmed_gesture = "WAITING"


        # ====================================================
        # CLOSED FIST → MUTE
        # ====================================================

        if confirmed_gesture == "CLOSED_FIST":

            # Only trigger once
            if last_confirmed_gesture != "CLOSED_FIST":

                volume_control.SetMute(
                    1,
                    None
                )

                is_muted = True

                print("🔇 MUTE")

            last_confirmed_gesture = "CLOSED_FIST"


        # ====================================================
        # OPEN PALM → UNMUTE
        # ====================================================

        elif confirmed_gesture == "OPEN_PALM":

            # Only trigger once
            if last_confirmed_gesture != "OPEN_PALM":

                volume_control.SetMute(
                    0,
                    None
                )

                is_muted = False

                print("🔊 UNMUTE")

            last_confirmed_gesture = "OPEN_PALM"


        # ====================================================
        # VOLUME CONTROL
        # ====================================================

        elif confirmed_gesture == "VOLUME":

            # ------------------------------------------------
            # Thumb and index landmarks
            # ------------------------------------------------

            thumb = hand_landmarks[4]
            index = hand_landmarks[8]


            thumb_x = int(thumb.x * w)
            thumb_y = int(thumb.y * h)

            index_x = int(index.x * w)
            index_y = int(index.y * h)


            # ------------------------------------------------
            # Pixel distance
            # ------------------------------------------------

            distance = math.sqrt(
                (index_x - thumb_x) ** 2 +
                (index_y - thumb_y) ** 2
            )


            # ------------------------------------------------
            # Map distance to volume
            # ------------------------------------------------

            target_volume = np.interp(
                distance,
                [MIN_DISTANCE, MAX_DISTANCE],
                [0, 100]
            )


            # ------------------------------------------------
            # Smooth volume
            # ------------------------------------------------

            smoothed_volume = (
                SMOOTHING_FACTOR * target_volume
                + (1 - SMOOTHING_FACTOR) * smoothed_volume
            )


            smoothed_volume = np.clip(
                smoothed_volume,
                0,
                100
            )


            # ------------------------------------------------
            # Unmute when user starts adjusting volume
            # ------------------------------------------------

            if is_muted:

                volume_control.SetMute(
                    0,
                    None
                )

                is_muted = False


            # ------------------------------------------------
            # Set Windows volume
            # ------------------------------------------------

            volume_control.SetMasterVolumeLevelScalar(
                smoothed_volume / 100,
                None
            )


            # ------------------------------------------------
            # Draw thumb and index
            # ------------------------------------------------

            cv2.circle(
                frame,
                (thumb_x, thumb_y),
                10,
                (255, 0, 0),
                -1
            )

            cv2.circle(
                frame,
                (index_x, index_y),
                10,
                (255, 0, 0),
                -1
            )

            cv2.line(
                frame,
                (thumb_x, thumb_y),
                (index_x, index_y),
                (255, 0, 0),
                3
            )


            # ------------------------------------------------
            # Display distance
            # ------------------------------------------------

            distance_text = (
                f"Distance: {int(distance)} px"
            )


        else:

            # Keep distance display empty
            distance_text = "Distance: --"


        # ====================================================
        # TOP INFORMATION PANEL
        # ====================================================

        cv2.rectangle(
            frame,
            (10, 10),
            (390, 185),
            (30, 30, 30),
            -1
        )


        cv2.putText(
            frame,
            "HAND GESTURE CONTROL",
            (25, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )


        # ----------------------------------------------------
        # Volume text
        # ----------------------------------------------------

        if is_muted:

            volume_text = "Volume: MUTED"

        else:

            volume_text = (
                f"Volume: {int(smoothed_volume)}%"
            )


        cv2.putText(
            frame,
            volume_text,
            (25, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )


        # ----------------------------------------------------
        # Gesture text
        # ----------------------------------------------------

        if confirmed_gesture == "CLOSED_FIST":

            gesture_text = "Gesture: CLOSED FIST"

        elif confirmed_gesture == "OPEN_PALM":

            gesture_text = "Gesture: OPEN PALM"

        elif confirmed_gesture == "VOLUME":

            gesture_text = "Gesture: VOLUME CONTROL"

        elif confirmed_gesture == "WAITING":

            gesture_text = "Gesture: DETECTING..."

        else:

            gesture_text = "Gesture: --"


        cv2.putText(
            frame,
            gesture_text,
            (25, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )


        # ----------------------------------------------------
        # Distance
        # ----------------------------------------------------

        cv2.putText(
            frame,
            distance_text,
            (25, 140),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (200, 200, 200),
            1
        )


        # ----------------------------------------------------
        # Action
        # ----------------------------------------------------

        if confirmed_gesture == "CLOSED_FIST":

            action_text = "Action: MUTE"

        elif confirmed_gesture == "OPEN_PALM":

            action_text = "Action: UNMUTE"

        elif confirmed_gesture == "VOLUME":

            action_text = "Action: ADJUST VOLUME"

        else:

            action_text = "Action: WAITING"


        cv2.putText(
            frame,
            action_text,
            (25, 170),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1
        )


        # ====================================================
        # VOLUME BAR
        # ====================================================

        bar_x = w - 70
        bar_y = 100

        bar_width = 35
        bar_height = 400


        cv2.rectangle(
            frame,
            (bar_x, bar_y),
            (bar_x + bar_width, bar_y + bar_height),
            (255, 255, 255),
            2
        )


        # ----------------------------------------------------
        # Display volume
        # ----------------------------------------------------

        if is_muted:

            display_volume = 0

        else:

            display_volume = smoothed_volume


        filled_height = int(
            bar_height * display_volume / 100
        )


        fill_top = (
            bar_y
            + bar_height
            - filled_height
        )


        cv2.rectangle(
            frame,
            (bar_x, fill_top),
            (bar_x + bar_width, bar_y + bar_height),
            (0, 255, 0),
            -1
        )


        cv2.putText(
            frame,
            f"{int(display_volume)}%",
            (bar_x - 20, bar_y + bar_height + 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )


    # ========================================================
    # NO HAND
    # ========================================================

    else:

        detected_gesture = "NONE"
        gesture_counter = 0
        last_confirmed_gesture = "NONE"


        cv2.rectangle(
            frame,
            (10, 10),
            (370, 80),
            (30, 30, 30),
            -1
        )


        cv2.putText(
            frame,
            "NO HAND DETECTED",
            (25, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )


        cv2.putText(
            frame,
            "Show your hand to the camera",
            (20, h - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )


    # ========================================================
    # QUIT
    # ========================================================

    cv2.putText(
        frame,
        "Q: Quit",
        (w - 120, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1
    )


    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.imshow(
        "Hand Gesture Volume Control",
        frame
    )


    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()
cv2.destroyAllWindows()
detector.close()

print("👋 Hand Gesture Volume Control stopped.")