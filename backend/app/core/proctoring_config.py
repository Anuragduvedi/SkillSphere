"""
SkillSphere Proctoring Configuration
Defines centralized thresholds, strike limits, and timing policies for AI-based camera proctoring.
"""

# Maximum permitted strikes before automatic examination termination
MAX_PROCTORING_STRIKES = 3

# Debounce window in seconds for non-critical identical events
PROCTORING_DEBOUNCE_SECONDS = 2.0

# Detection confidence thresholds
FACE_DETECTION_MIN_CONFIDENCE = 0.42
PHONE_DETECTION_SCORE_THRESHOLD = 0.45

# Timing rules (in milliseconds for frontend reference and backend consistency)
FACE_MISSING_WARNING_MS = 2000     # 2 seconds face missing -> immediate UI warning
FACE_MISSING_STRIKE_MS = 5000      # 5 seconds face missing -> serious violation / strike
MULTIPLE_FACES_WARNING_MS = 500    # 0.5 seconds multiple faces -> immediate warning
MULTIPLE_FACES_TERMINATE_MS = 2000 # 2 continuous seconds with multiple faces -> instant termination!
PHONE_CONTINUOUS_STRIKE_MS = 2000  # 2 continuous seconds phone visible -> serious violation / strike

# Permitted event types
ALLOWED_PROCTORING_EVENTS = [
    "face_not_detected",
    "tab_switch",
    "window_blur",
    "camera_interrupted",
    "phone_detected",
    "multiple_faces",
    "looking_away",
    "fullscreen_exit",
    "instant_terminate"
]

# Critical events that bypass minor debounce rules and can cause immediate termination
CRITICAL_PROCTORING_EVENTS = [
    "multiple_faces",
    "phone_detected",
    "instant_terminate"
]
