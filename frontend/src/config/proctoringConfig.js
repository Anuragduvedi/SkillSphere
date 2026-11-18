/**
 * SkillSphere AI Proctoring Configuration
 * Centralized settings for MediaPipe Face & Object Detectors, violation thresholds, and strike policies.
 */

export const PROCTORING_CONFIG = {
  // Face Detection (MediaPipe BlazeFace)
  face: {
    minDetectionConfidence: 0.42,
    detectionIntervalMs: 180, // Evaluates ~5.5 fps to avoid main-thread freeze
    missingWarningDurationMs: 2000, // 2s missing -> immediate visual alert
    missingViolationDurationMs: 5000, // 5s missing -> record strike to backend
    multipleWarningDurationMs: 500, // Immediate alert upon detecting > 1 face
    multipleTerminationDurationMs: 2000, // 2s multiple faces -> terminate assessment!
  },

  // Mobile Phone Detection (MediaPipe EfficientDet Lite0)
  phone: {
    scoreThreshold: 0.45,
    detectionIntervalMs: 250, // Evaluates 4 fps for object detector
    warningImmediate: true, // Show immediate visual alert on first detection
    continuousViolationDurationMs: 2000, // 2s phone visible -> record strike to backend
    categoryAllowlist: ['cell phone', 'mobile phone', 'telephone'],
  },

  // General Proctoring Policies
  policy: {
    maxStrikes: 3,
    notificationCooldownMs: 2500, // Debounce alert banner / toast messages
    minEventDebounceMs: 1500, // Debounce duplicate event logging to backend
  },
};

export default PROCTORING_CONFIG;
