
import { FilesetResolver, FaceDetector, ObjectDetector } from '@mediapipe/tasks-vision';
import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Clock,
  AlertCircle,
  CheckCircle2,
  XCircle,
  ArrowRight,
  ArrowLeft,
  Send,
  Sparkles,
  ShieldAlert,
  Award,
  FileText,
  ChevronDown,
  ChevronUp,
  BrainCircuit,
  Lock,
  Building2,
  Briefcase,
  Smartphone
} from 'lucide-react';
import { assessmentAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { PROCTORING_CONFIG } from '../config/proctoringConfig';

export default function AssessmentPage() {
  const { token } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { showToast: addToast } = useToast();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [assessment, setAssessment] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(25 * 60);
  const [testStarted, setTestStarted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [terminationReason, setTerminationReason] = useState('');
  const [violationCount, setViolationCount] = useState(0);
  const [showProctoringWarning, setShowProctoringWarning] = useState(false);
  const [proctoringWarningLevel, setProctoringWarningLevel] = useState(0);
  const [proctoringWarningDetails, setProctoringWarningDetails] = useState('');
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [expandedQuestions, setExpandedQuestions] = useState({});
  const [immediateAlert, setImmediateAlert] = useState(null);

  const timerRef = useRef(null);

  // Camera and proctoring references
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const detectorRef = useRef(null);
  const objectDetectorRef = useRef(null);
  const animationFrameRef = useRef(null);
  const lastEventTimesRef = useRef({});
  const answersRef = useRef(answers);
  answersRef.current = answers;

  // Proctoring detection state machines and timers
  const faceMissingSinceRef = useRef(null);
  const faceMissingWarningTriggeredRef = useRef(false);
  const faceMissingStrikeTriggeredRef = useRef(false);

  const multipleFacesSinceRef = useRef(null);
  const multipleFacesWarningTriggeredRef = useRef(false);

  const phoneDetectedSinceRef = useRef(null);
  const phoneWarningTriggeredRef = useRef(false);
  const phoneStrikeTriggeredRef = useRef(false);

  const lookingAwaySinceRef = useRef(null);
  const lastFaceCheckAtRef = useRef(0);
  const lastObjectDetectionAtRef = useRef(0);
  const isProcessingRef = useRef(false);
  const isTerminatingRef = useRef(false);

  const [cameraGranted, setCameraGranted] = useState(false);
  const [cameraError, setCameraError] = useState('');
  const [detectorReady, setDetectorReady] = useState(false);
  const [facePresent, setFacePresent] = useState(false);
  const [faceCount, setFaceCount] = useState(0);
  const [phoneDetected, setPhoneDetected] = useState(false);
  const [objectDetectorReady, setObjectDetectorReady] = useState(false);
  const [startingTest, setStartingTest] = useState(false);

  // Video element attachment callback to ensure stream persists across view transitions
  const attachVideoRef = (el) => {
    videoRef.current = el;
    if (el && streamRef.current && el.srcObject !== streamRef.current) {
      el.srcObject = streamRef.current;
      el.play().catch((err) => {
        console.warn('Webcam video play interrupted:', err);
      });
    }
  };

  // Re-synchronize camera video stream whenever test starts
  useEffect(() => {
    if (videoRef.current && streamRef.current && videoRef.current.srcObject !== streamRef.current) {
      videoRef.current.srcObject = streamRef.current;
      videoRef.current.play().catch(() => {});
    }
  }, [testStarted]);

  // Initialize MediaPipe face detector and COCO object detector
  useEffect(() => {
    let cancelled = false;

    const initializeDetector = async () => {
      try {
        const vision = await FilesetResolver.forVisionTasks(
          'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@1.2.3/wasm'
        );

        const detector = await FaceDetector.createFromOptions(vision, {
          baseOptions: {
            modelAssetPath:
              'https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite',
            delegate: 'CPU',
          },
          runningMode: 'VIDEO',
          minDetectionConfidence: PROCTORING_CONFIG.face.minDetectionConfidence,
        });

        if (cancelled) {
          detector.close();
          return;
        }

        detectorRef.current = detector;
        setDetectorReady(true);

        // Separate COCO object detector for mobile phone detection
        try {
          const objectDetector = await ObjectDetector.createFromOptions(vision, {
            baseOptions: {
              modelAssetPath:
                'https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/float32/1/efficientdet_lite0.tflite',
              delegate: 'CPU',
            },
            runningMode: 'VIDEO',
            scoreThreshold: PROCTORING_CONFIG.phone.scoreThreshold,
            categoryAllowlist: PROCTORING_CONFIG.phone.categoryAllowlist,
          });

          if (cancelled) {
            objectDetector.close();
            return;
          }

          objectDetectorRef.current = objectDetector;
          setObjectDetectorReady(true);
        } catch (objectError) {
          console.error('Phone detector initialization failed:', objectError);
        }
      } catch (error) {
        console.error('Face detector initialization failed:', error);
        setCameraError('Face detection could not be initialized. Please refresh the page.');
      }
    };

    initializeDetector();

    return () => {
      cancelled = true;
      detectorRef.current?.close();
      detectorRef.current = null;
      objectDetectorRef.current?.close();
      objectDetectorRef.current = null;
    };
  }, []);


// Request camera permission when assessment loads
useEffect(() => {
  if (loading || !assessment || result) return;

  let cancelled = false;

  const requestCamera = async () => {
    let stream;

    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        throw new Error("Camera access is not supported on this browser.");
      }

      console.log("Requesting camera access...");

      stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "user",
          width: { ideal: 640 },
          height: { ideal: 480 },
        },
        audio: false,
      });

      if (cancelled) {
        stream.getTracks().forEach(track => track.stop());
        return;
      }

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.muted = true;
        videoRef.current.playsInline = true;
        videoRef.current.play().catch(err => {
          console.warn("Camera auto-play deferred:", err);
        });
      }

      setCameraGranted(true);
      setCameraError("");

    } catch (error) {
      console.error("Camera initialization failed:", error);

      if (stream && stream !== streamRef.current) {
        stream.getTracks().forEach(track => track.stop());
      }

      if (!cancelled) {
        setCameraGranted(false);
        setCameraError(`${error.name}: ${error.message}`);
      }
    }
  };

  requestCamera();

  return () => {
    cancelled = true;
  };
}, [loading, assessment, result]);


// Stop camera and cancel animation frame when component is unmounted
useEffect(() => {
  return () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
  };
}, []);

// Immediate assessment termination due to severe proctoring breach
const terminateAssessmentDueToViolation = async (eventType, reason) => {
  if (isTerminatingRef.current) return;
  isTerminatingRef.current = true;

  // Immediately stop all hardware and timers
  if (streamRef.current) {
    streamRef.current.getTracks().forEach(track => track.stop());
    streamRef.current = null;
  }
  if (animationFrameRef.current) {
    cancelAnimationFrame(animationFrameRef.current);
    animationFrameRef.current = null;
  }
  if (timerRef.current) {
    clearInterval(timerRef.current);
    timerRef.current = null;
  }

  setTestStarted(false);
  setTerminationReason(reason);
  setViolationCount(3);
  setImmediateAlert(null);
  addToast(reason, 'error');

  try {
    await assessmentAPI.recordProctoringEvent(
      assessment.assessment_id,
      eventType,
      reason,
      answersRef.current,
      { instant_terminate: true, severity: 'critical' }
    );
  } catch (error) {
    console.error('Failed to notify backend of assessment termination:', error);
  }
};

// Record proctoring events with strike tracking and debouncing
const logProctoringEvent = async (eventType, details, options = {}) => {
  if (!assessment?.assessment_id || !testStarted || isTerminatingRef.current) return;

  const now = Date.now();
  const lastTime = lastEventTimesRef.current[eventType] || 0;
  const isInstant = options.instant_terminate || false;
  const isCritical = options.severity === 'critical';

  // Respect minimum debounce window only for non-critical warnings
  if (!isInstant && !isCritical) {
    if (now - lastTime < PROCTORING_CONFIG.policy.minEventDebounceMs) return;
  }
  lastEventTimesRef.current[eventType] = now;

  try {
    const response = await assessmentAPI.recordProctoringEvent(
      assessment.assessment_id,
      eventType,
      details,
      answersRef.current,
      options
    );

    const data = response.data;
    if (data.duplicate) return;

    if (typeof data.strikes === 'number') {
      setViolationCount(data.strikes);
    }

    if (data.terminated) {
      isTerminatingRef.current = true;
      setTestStarted(false);
      setImmediateAlert(null);
      const finalMsg = data.warning || details || 'Your assessment has been terminated due to proctoring policy enforcement.';
      setTerminationReason(finalMsg);
      addToast(finalMsg, 'error');

      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
      return;
    }

    if (data.strikes === 1 || data.strikes === 2) {
      setProctoringWarningLevel(data.strikes);
      setProctoringWarningDetails(details || 'Proctoring violation recorded.');
      setShowProctoringWarning(true);
    }

  } catch (error) {
    console.error('Failed to save proctoring event:', error);
  }
};


// Monitor face count, multiple individuals, and mobile phones during active exam
useEffect(() => {
  if (!testStarted || !cameraGranted || !detectorReady) return;

  let stopped = false;
  let lastVideoTime = -1;

  const detectFrame = () => {
    if (stopped || isTerminatingRef.current) return;

    const video = videoRef.current;
    const faceDetector = detectorRef.current;
    const objectDetector = objectDetectorRef.current;

    if (
      video &&
      faceDetector &&
      video.readyState >= 2 &&
      video.videoWidth > 0 &&
      video.videoHeight > 0 &&
      !video.paused &&
      !isProcessingRef.current
    ) {
      const now = performance.now();

      // Run face detection according to configured interval
      if (now - lastFaceCheckAtRef.current >= PROCTORING_CONFIG.face.detectionIntervalMs) {
        lastFaceCheckAtRef.current = now;
        isProcessingRef.current = true;

        try {
          const detections = faceDetector.detectForVideo(video, now).detections || [];
          const count = detections.length;
          setFaceCount(count);
          setFacePresent(count === 1);

          // EXACTLY 1 FACE: Compliant state
          if (count === 1) {
            faceMissingSinceRef.current = null;
            faceMissingWarningTriggeredRef.current = false;
            faceMissingStrikeTriggeredRef.current = false;

            multipleFacesSinceRef.current = null;
            multipleFacesWarningTriggeredRef.current = false;

            setImmediateAlert(prev => (prev?.category === 'face' ? null : prev));

            // Secondary telemetry: Check looking away
            if (detections[0]?.keypoints && detections[0].keypoints.length >= 3) {
              const kp = detections[0].keypoints;
              const rightEye = kp[0];
              const leftEye = kp[1];
              const nose = kp[2];
              if (rightEye && leftEye && nose) {
                const eyeDist = Math.abs(rightEye.x - leftEye.x);
                const eyeMidX = (rightEye.x + leftEye.x) / 2;
                if (eyeDist > 0.035) {
                  const yawOffset = Math.abs(nose.x - eyeMidX) / eyeDist;
                  if (yawOffset > 0.55) {
                    if (lookingAwaySinceRef.current === null) lookingAwaySinceRef.current = now;
                    if (now - lookingAwaySinceRef.current >= 3500) {
                      logProctoringEvent(
                        'looking_away',
                        'Candidate was observed looking away from the assessment screen for extended duration.'
                      );
                    }
                  } else {
                    lookingAwaySinceRef.current = null;
                  }
                } else {
                  lookingAwaySinceRef.current = null;
                }
              }
            }
          }
          // ZERO FACES: Face Missing State
          else if (count === 0) {
            lookingAwaySinceRef.current = null;
            multipleFacesSinceRef.current = null;
            multipleFacesWarningTriggeredRef.current = false;

            if (faceMissingSinceRef.current === null) {
              faceMissingSinceRef.current = now;
            }
            const missingDuration = now - faceMissingSinceRef.current;

            // Immediate visual warning at 2 continuous seconds
            if (missingDuration >= PROCTORING_CONFIG.face.missingWarningDurationMs) {
              setImmediateAlert({
                category: 'face',
                type: 'warning',
                title: 'Face Not Detected',
                message: 'Your face is not clearly visible in the camera frame. Please reposition immediately.'
              });

              if (!faceMissingWarningTriggeredRef.current) {
                faceMissingWarningTriggeredRef.current = true;
                addToast('Warning: Face not detected! Please ensure your face is clearly visible.', 'warning');
              }
            }

            // Serious violation strike at 5 continuous seconds
            if (missingDuration >= PROCTORING_CONFIG.face.missingViolationDurationMs && !faceMissingStrikeTriggeredRef.current) {
              faceMissingStrikeTriggeredRef.current = true;
              logProctoringEvent(
                'face_not_detected',
                'No face was detected in the camera frame for 5 continuous seconds.',
                { severity: 'warning' }
              );
            }
          }
          // MULTIPLE FACES: Severe violation (> 1 face)
          else if (count > 1) {
            lookingAwaySinceRef.current = null;
            faceMissingSinceRef.current = null;
            faceMissingWarningTriggeredRef.current = false;
            faceMissingStrikeTriggeredRef.current = false;

            if (multipleFacesSinceRef.current === null) {
              multipleFacesSinceRef.current = now;
            }
            const multipleDuration = now - multipleFacesSinceRef.current;

            // Immediate visual alert
            setImmediateAlert({
              category: 'face',
              type: 'danger',
              title: 'Multiple People Detected',
              message: `Multiple faces (${count}) detected! Only the assigned candidate may be present. Examination will terminate if this persists!`
            });

            if (!multipleFacesWarningTriggeredRef.current) {
              multipleFacesWarningTriggeredRef.current = true;
              addToast(`Violation Warning: ${count} faces detected in front of camera!`, 'error');
            }

            // AUTOMATIC TERMINATION IF MULTIPLE FACES REMAIN FOR >= 2 SECONDS!
            if (multipleDuration >= PROCTORING_CONFIG.face.multipleTerminationDurationMs && !isTerminatingRef.current) {
              terminateAssessmentDueToViolation(
                'multiple_faces',
                `Your assessment was automatically terminated because multiple people (${count} faces) were detected in front of the camera for more than 2 seconds.`
              );
              return;
            }
          }

          // MOBILE PHONE DETECTION
          if (objectDetector && now - lastObjectDetectionAtRef.current >= PROCTORING_CONFIG.phone.detectionIntervalMs) {
            lastObjectDetectionAtRef.current = now;
            const objects = objectDetector.detectForVideo(video, now).detections || [];
            let maxPhoneScore = 0;
            const hasPhone = objects.some((item) =>
              (item.categories || []).some((category) => {
                const name = String(category.categoryName || '').toLowerCase();
                const score = category.score || 0;
                if (
                  PROCTORING_CONFIG.phone.categoryAllowlist.some(allowed => name.includes(allowed)) &&
                  score >= PROCTORING_CONFIG.phone.scoreThreshold
                ) {
                  maxPhoneScore = Math.max(maxPhoneScore, score);
                  return true;
                }
                return false;
              })
            );

            setPhoneDetected(hasPhone);

            if (hasPhone) {
              if (phoneDetectedSinceRef.current === null) {
                phoneDetectedSinceRef.current = now;
              }
              const phoneDuration = now - phoneDetectedSinceRef.current;

              // Immediate warning on first confirmed detection
              setImmediateAlert({
                category: 'phone',
                type: 'danger',
                title: 'Mobile Phone Detected',
                message: 'A mobile phone was detected! Mobile devices are strictly prohibited during the assessment.'
              });

              if (!phoneWarningTriggeredRef.current) {
                phoneWarningTriggeredRef.current = true;
                addToast('URGENT: Mobile phone detected! Please remove the mobile device immediately.', 'error');
              }

              // Record serious violation if phone remains visible for >= 2 seconds
              if (phoneDuration >= PROCTORING_CONFIG.phone.continuousViolationDurationMs && !phoneStrikeTriggeredRef.current) {
                phoneStrikeTriggeredRef.current = true;
                logProctoringEvent(
                  'phone_detected',
                  `A mobile phone was detected in front of the camera for >= 2 seconds (confidence: ${maxPhoneScore.toFixed(2)}).`,
                  { severity: 'critical', confidence: maxPhoneScore }
                );
              }
            } else {
              phoneDetectedSinceRef.current = null;
              phoneWarningTriggeredRef.current = false;
              phoneStrikeTriggeredRef.current = false;
              setImmediateAlert(prev => (prev?.category === 'phone' ? null : prev));
            }
          }

        } catch (detectionErr) {
          console.error('Proctoring detection loop error:', detectionErr);
        } finally {
          isProcessingRef.current = false;
        }
      }
    }

    if (!stopped && !isTerminatingRef.current) {
      animationFrameRef.current = requestAnimationFrame(detectFrame);
    }
  };

  animationFrameRef.current = requestAnimationFrame(detectFrame);

  return () => {
    stopped = true;
    if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    faceMissingSinceRef.current = null;
    multipleFacesSinceRef.current = null;
    phoneDetectedSinceRef.current = null;
    lookingAwaySinceRef.current = null;
  };
}, [testStarted, cameraGranted, detectorReady, objectDetectorReady]);
// Monitor tab switching and window focus
useEffect(() => {
  if (!testStarted) return;

  const handleVisibilityChange = () => {
  if (document.hidden) {
    logProctoringEvent(
      'tab_switch',
      'Candidate switched away from the assessment tab.'
    );

    if (typeof addToast === 'function') {
      addToast(
        'Warning: Please do not switch tabs during the assessment.',
        'warning'
      );
    } else {
      console.warn(
        'Warning: Please do not switch tabs during the assessment.'
      );
    }
  }
};

  document.addEventListener('visibilitychange', handleVisibilityChange);

  return () => {
    document.removeEventListener('visibilitychange', handleVisibilityChange);
  };
}, [testStarted]);

// Deter common copy/paste shortcuts and record leaving fullscreen.
useEffect(() => {
  if (!testStarted) return;

  const preventClipboard = (event) => {
    event.preventDefault();
    addToast('Copying and pasting are disabled during the assessment.', 'warning');
  };

  const preventContextMenu = (event) => event.preventDefault();
  const preventShortcut = (event) => {
    const key = String(event.key || '').toLowerCase();
    if ((event.ctrlKey || event.metaKey) && ['c', 'v', 'x', 'a'].includes(key)) {
      event.preventDefault();
      addToast('Clipboard shortcuts are disabled during the assessment.', 'warning');
    }
  };
  const handleFullscreenChange = () => {
    if (!document.fullscreenElement) {
      logProctoringEvent('fullscreen_exit', 'Candidate exited fullscreen during the assessment.');
    }
  };

  document.addEventListener('copy', preventClipboard);
  document.addEventListener('cut', preventClipboard);
  document.addEventListener('paste', preventClipboard);
  document.addEventListener('contextmenu', preventContextMenu);
  document.addEventListener('keydown', preventShortcut);
  document.addEventListener('fullscreenchange', handleFullscreenChange);

  return () => {
    document.removeEventListener('copy', preventClipboard);
    document.removeEventListener('cut', preventClipboard);
    document.removeEventListener('paste', preventClipboard);
    document.removeEventListener('contextmenu', preventContextMenu);
    document.removeEventListener('keydown', preventShortcut);
    document.removeEventListener('fullscreenchange', handleFullscreenChange);
  };
}, [testStarted]);


// Monitor camera interruption
useEffect(() => {
  if (!testStarted || !streamRef.current) return;

  const tracks = streamRef.current.getVideoTracks();

  const handleCameraEnded = () => {
    logProctoringEvent(
      'camera_interrupted',
      'Camera stream was interrupted or stopped.'
    );

    setCameraGranted(false);

    addToast(
      'Warning: Camera connection was interrupted.',
      'error'
    );
  };

  tracks.forEach(track => {
    track.addEventListener('ended', handleCameraEnded);
  });

  return () => {
    tracks.forEach(track => {
      track.removeEventListener('ended', handleCameraEnded);
    });
  };
}, [testStarted]);

const handleStartTest = async () => {
  console.log("START FUNCTION CALLED");
  console.log("Assessment:", assessment);

  if (!cameraGranted || !detectorReady || startingTest) {
    console.log("Start blocked by conditions");
    return;
  }

  setStartingTest(true);

  try {
    if (document.documentElement.requestFullscreen && !document.fullscreenElement) {
      try {
        await document.documentElement.requestFullscreen();
      } catch (fullscreenError) {
        console.warn('Fullscreen could not be enabled:', fullscreenError);
      }
    }

    console.log("Calling backend start API...");

    const response = await assessmentAPI.start(assessment.assessment_id);

    console.log("START API SUCCESS:", response.data);

    setTestStarted(true);
    addToast("Assessment started. Camera monitoring is active.", "success");

  } catch (error) {
    console.error("START API ERROR:", error);
    addToast(
      error.response?.data?.detail || "Unable to start assessment. Please ensure your assessment link is active.",
      "error"
    );

  } finally {
    setStartingTest(false);
  }
};


  // 1. Fetch Assessment by Token
  useEffect(() => {
    async function fetchAssessment() {
      try {
        setLoading(true);
        setError(null);
       const res = await assessmentAPI.getByToken(token);
const data = res.data;
setAssessment(data);

if (data.status === 'terminated_proctoring') {

  setTerminationReason(
    'Your assessment was terminated due to three proctoring violations.'
  );

  setViolationCount(3);

} else if (data.status === 'completed') {

  // Keep your existing completed results code here
          try {
            const resultsRes = await assessmentAPI.getResults(data.assessment_id);
            setResult(resultsRes.data);
          } catch (rErr) {
            setResult({
              assessment_id: data.assessment_id,
              score: data.score,
              total_questions: data.total_questions || 20,
              percentage: data.percentage,
              passed: data.passed,
              breakdown: []
            });
          }
        } else {
          setQuestions(data.questions || []);
          const totalSecs = (data.time_limit_minutes || 25) * 60;
          setTimeLeft(totalSecs);
        }
      } catch (err) {
        console.error('Failed to load assessment:', err);
        setError(
          err.response?.data?.detail ||
          'Failed to load technical assessment. Please verify your access link or log in as the assigned candidate.'
        );
      } finally {
        setLoading(false);
      }
    }

    if (token) {
      fetchAssessment();
    }
  }, [token]);

  // 2. Countdown Timer
  useEffect(() => {
    if (!testStarted || result || timeLeft <= 0) return;

    timerRef.current = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timerRef.current);
          handleAutoSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timerRef.current);
  }, [testStarted, result]);

  // Format MM:SS
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Select Option
  const handleSelectOption = (questionId, option) => {
    if (result) return;
    setAnswers((prev) => ({
      ...prev,
      [questionId]: option,
    }));
  };

  // Auto-submit when time expires
  const handleAutoSubmit = () => {
    addToast('Time limit reached! Automatically submitting your assessment...', 'warning');
    handleSubmitAnswers();
  };

  // Submit answers to API
  const handleSubmitAnswers = async () => {
    if (!assessment) return;
    setIsSubmitting(true);
    setShowConfirmModal(false);

    try {
      const res = await assessmentAPI.submit(assessment.assessment_id, answersRef.current);
      setResult(res.data);
      addToast(`Assessment completed! Score: ${res.data.score}/${res.data.total_questions} (${res.data.percentage}%)`, 'success');
    } catch (err) {
      console.error('Submission error:', err);
      addToast(err.response?.data?.detail || 'Failed to submit assessment.', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleExpand = (qId) => {
    setExpandedQuestions((prev) => ({
      ...prev,
      [qId]: !prev[qId],
    }));
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-[80vh] flex flex-col items-center justify-center p-6">
        <div className="w-12 h-12 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin mb-4" />
        <p className="text-slate-400 font-medium">Securing test environment & loading technical questions...</p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="max-w-xl mx-auto my-16 p-8 glass-card border-rose-500/30 text-center">
        <ShieldAlert className="w-14 h-14 text-rose-400 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-white mb-2">Access Restricted</h2>
        <p className="text-slate-300 mb-6">{error}</p>
        <div className="flex justify-center gap-4">
          <Link
            to="/login"
            className="px-6 py-2.5 rounded-xl bg-cyan-500 text-black font-semibold hover:bg-cyan-400 transition-colors"
          >
            Sign In with Candidate Account
          </Link>
          <Link
            to="/dashboard"
            className="px-6 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-medium transition-colors"
          >
            Return to Dashboard
          </Link>
        </div>
      </div>
    );
  }
// TERMINATED ASSESSMENT VIEW
if (terminationReason) {
  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card max-w-lg w-full p-8 text-center border border-rose-500/30"
      >
        <ShieldAlert className="w-16 h-16 text-rose-500 mx-auto mb-4" />

        <h1 className="text-2xl font-bold text-rose-400 mb-3">
          Assessment Terminated
        </h1>

        <p className="text-slate-300 mb-4">
          {terminationReason}
        </p>

        <p className="font-semibold text-white mb-4">
          Proctoring Violations: {violationCount}/3
        </p>

        <p className="text-sm text-slate-400 mb-6">
          Your assessment has been stopped due to repeated proctoring violations.
        </p>

        <Link
          to="/dashboard"
          className="inline-block px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-black font-bold"
        >
          Return to Dashboard
        </Link>
      </motion.div>
    </div>
  );
}
  // COMPLETED RESULTS VIEW
  if (result) {
    const isPassed = result.passed;
    const answeredCount = Object.keys(answers).length;

    return (
      <div className="max-w-5xl mx-auto px-4 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-8 mb-8 border border-white/10"
        >
          {/* Header Badge */}
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 pb-6 border-b border-white/10">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 mb-3">
                <BrainCircuit className="w-3.5 h-3.5" />
                Assessment Results Summary
              </div>
              <h1 className="text-3xl font-extrabold text-white tracking-tight">{result.title || assessment?.title}</h1>
              <p className="text-slate-400 mt-1 flex items-center gap-3">
                <span className="flex items-center gap-1.5"><Briefcase className="w-4 h-4 text-cyan-400" /> {result.job_title || assessment?.job_title}</span>
                <span>•</span>
                <span className="flex items-center gap-1.5"><Building2 className="w-4 h-4 text-slate-400" /> {result.company_name || assessment?.company_name}</span>
              </p>
            </div>

            {/* Score Pill */}
            <div className={`flex items-center gap-4 p-4 rounded-2xl border ${isPassed ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-rose-500/10 border-rose-500/30'}`}>
              <div className={`w-14 h-14 rounded-full flex items-center justify-center font-extrabold text-xl ${isPassed ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                {result.score}/{result.total_questions}
              </div>
              <div>
                <p className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Total Score</p>
                <p className={`text-2xl font-black ${isPassed ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {result.percentage}%
                </p>
                <span className={`inline-block px-2 py-0.5 mt-1 rounded text-xs font-bold ${isPassed ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'}`}>
                  {isPassed ? 'Passed (Interview Qualified)' : 'Under Review'}
                </span>
              </div>
            </div>
          </div>

          {/* Feedback note */}
          <div className="mt-6 p-4 rounded-xl bg-white/5 border border-white/10 flex items-start gap-3">
            <Sparkles className="w-5 h-5 text-cyan-400 mt-0.5 shrink-0" />
            <div>
              <h4 className="text-sm font-semibold text-white">Automated AI Evaluation Verdict</h4>
              <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                {isPassed
                  ? `Congratulations! You scored ${result.score} out of ${result.total_questions} (${result.percentage}%), meeting the technical competence threshold (60%+). Your application has automatically transitioned to the 'Interview' pipeline stage.`
                  : `You scored ${result.score} out of ${result.total_questions} (${result.percentage}%). While below the immediate 60% automated qualification mark, your answers have been preserved and forwarded to the recruiting team for secondary portfolio review.`}
              </p>
            </div>
          </div>
        </motion.div>

        {/* Detailed Question Review */}
        {result.breakdown && result.breakdown.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <FileText className="w-5 h-5 text-cyan-400" />
                Comprehensive 20-Question Breakdown & Explanations
              </h3>
              <span className="text-xs text-slate-400">
                {result.correct_answers_count ?? result.score} Correct • {(result.total_questions || 20) - (result.correct_answers_count ?? result.score)} Incorrect
              </span>
            </div>

            {result.breakdown.map((q, idx) => {
              const isCorrect = q.is_correct;
              const isExpanded = !!expandedQuestions[q.question_id];

              return (
                <div
                  key={q.question_id || idx}
                  className={`glass-card p-6 border transition-all ${
                    isCorrect ? 'border-emerald-500/20 hover:border-emerald-500/40' : 'border-rose-500/20 hover:border-rose-500/40'
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3">
                      <div className={`mt-0.5 p-1 rounded-full ${isCorrect ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                        {isCorrect ? <CheckCircle2 className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
                      </div>
                      <div>
                        <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                          <span className="text-xs font-bold text-slate-400">Q{idx + 1}</span>
                          <span className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider bg-white/10 text-slate-300">
                            {q.skill_category}
                          </span>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider ${
                            q.difficulty === 'beginner' ? 'bg-cyan-500/10 text-cyan-400' :
                            q.difficulty === 'intermediate' ? 'bg-purple-500/10 text-purple-400' :
                            'bg-amber-500/10 text-amber-400'
                          }`}>
                            {q.difficulty}
                          </span>
                        </div>
                        <h4 className="text-base font-semibold text-white leading-snug">{q.question_text}</h4>
                      </div>
                    </div>

                    <button
                      onClick={() => toggleExpand(q.question_id)}
                      className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
                    >
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                  </div>

                  {/* Answers overview */}
                  <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                    <div className={`p-3 rounded-xl border ${isCorrect ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-rose-500/10 border-rose-500/30 text-rose-300'}`}>
                      <span className="font-semibold block mb-0.5">Your Submitted Answer:</span>
                      <span>{q.candidate_answer || '(Unanswered)'}</span>
                    </div>

                    {!isCorrect && (
                      <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
                        <span className="font-semibold block mb-0.5">Correct Answer:</span>
                        <span>{q.correct_answer}</span>
                      </div>
                    )}
                  </div>

                  {/* Explanation drawer */}
                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mt-4 pt-4 border-t border-white/10 text-xs text-slate-300"
                      >
                        <p className="font-semibold text-white mb-1 flex items-center gap-1.5">
                          <BrainCircuit className="w-3.5 h-3.5 text-cyan-400" />
                          Technical Solution & Concept Explanation:
                        </p>
                        <p className="leading-relaxed bg-black/30 p-3 rounded-lg border border-white/5 font-mono text-slate-300">
                          {q.explanation || 'No specific explanation provided for this question.'}
                        </p>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              );
            })}
          </div>
        )}

        <div className="mt-10 flex justify-center">
          <Link
            to="/dashboard"
            className="px-8 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-black font-bold hover:shadow-cyan-500/25 shadow-lg transition-all"
          >
            Return to Candidate Dashboard
          </Link>
        </div>
      </div>
    );
  }

  // INSTRUCTIONS MODAL / INTRO SCREEN
  if (!testStarted) {
    return (
      <div className="max-w-3xl mx-auto my-12 px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-card p-8 border border-white/10 shadow-2xl relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/10 blur-[100px] pointer-events-none" />

          <div className="flex items-center gap-3 mb-4">
            <span className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <BrainCircuit className="w-6 h-6" />
            </span>
            <div>
              <span className="text-xs uppercase font-bold tracking-wider text-cyan-400">SkillSphere AI Assessment</span>
              <h1 className="text-2xl font-black text-white">{assessment?.title}</h1>
            </div>
          </div>

          <p className="text-sm text-slate-300 leading-relaxed mb-6">
            You have been automatically shortlisted for this role based on your profile and resume fit. 
            This technical assessment dynamically measures your proficiency across the key skills required for this job.
          </p>

          {/* Test Specs Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
            <div className="glass-card p-4 text-center border-white/5">
              <span className="text-xs text-slate-400 block mb-1">Total Questions</span>
              <span className="text-xl font-black text-white">{questions.length || 20}</span>
              <span className="text-[10px] text-slate-500 block mt-0.5">MCQ Format</span>
            </div>
            <div className="glass-card p-4 text-center border-white/5">
              <span className="text-xs text-slate-400 block mb-1">Time Limit</span>
              <span className="text-xl font-black text-cyan-400">{assessment?.time_limit_minutes || 25} Mins</span>
              <span className="text-[10px] text-slate-500 block mt-0.5">Timed session</span>
            </div>
            <div className="glass-card p-4 text-center border-white/5">
              <span className="text-xs text-slate-400 block mb-1">Difficulty</span>
              <span className="text-xl font-black text-purple-400">Adaptive</span>
              <span className="text-[10px] text-slate-500 block mt-0.5">Beg / Int / Adv</span>
            </div>
            <div className="glass-card p-4 text-center border-white/5">
              <span className="text-xs text-slate-400 block mb-1">Passing Mark</span>
              <span className="text-xl font-black text-emerald-400">60%</span>
              <span className="text-[10px] text-slate-500 block mt-0.5">12 / 20 correct</span>
            </div>
          </div>

          {/* Guidelines */}
          <div className="space-y-3 p-5 rounded-2xl bg-white/5 border border-white/10 mb-8 text-xs text-slate-300">
            <h4 className="font-semibold text-white flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-cyan-400" />
              Examination Rules & Integrity:
            </h4>
            <ul className="list-disc list-inside space-y-1.5 text-slate-300">
              <li>Each question has exactly 4 options with one single correct answer.</li>
              <li>Questions and answer options have been randomized for this attempt.</li>
              <li>Once you click Start, the 25-minute timer cannot be paused.</li>
              <li>You can navigate between questions and review your selected answers before submission.</li>
              <li>When the timer expires, all answered questions will be automatically evaluated.</li>
              <li>Only one attempt is permitted; duplicate submissions will be rejected by the portal.</li>
            </ul>
          </div>

          <div className="flex items-center justify-between gap-4 pt-2">
            <Link
              to="/dashboard"
              className="px-5 py-3 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 font-medium text-sm transition-colors"
            >
              Cancel & Exit
            </Link>
            {/* Camera Proctoring Status */}
<div className="mb-6 rounded-xl border border-cyan-500/30 bg-cyan-500/5 p-5">
 
<video
  ref={attachVideoRef}
  autoPlay
  playsInline
  muted
  className="w-full max-w-sm rounded-xl border border-blue-400 object-cover transform scale-x-[-1]"
  style={{ minHeight: "220px", background: "#111" }}
/>


  <h3 className="text-lg font-bold text-white mb-3">
    Camera Verification
  </h3>

  <p className="text-sm text-gray-300 mb-2">
    Camera: {cameraGranted ? 'Connected' : 'Waiting for permission'}
  </p>

  <p className="text-sm text-gray-300 mb-2">
    Face Detector: {detectorReady ? 'Ready' : 'Loading...'}
  </p>

  {cameraError && (
    <p className="text-sm text-red-400 mt-2">
      {cameraError}
    </p>
  )}

  <p className="text-xs text-gray-400 mt-3">
    Your camera is used for face monitoring. No video or images are stored.
  </p>
</div>
         <button
  onClick={handleStartTest}
  disabled={!cameraGranted || !detectorReady || startingTest}
  className={`px-8 py-3 rounded-xl font-bold transition-all flex items-center gap-2 text-sm ${
    cameraGranted && detectorReady && !startingTest
      ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-black hover:shadow-cyan-500/25 shadow-lg'
      : 'bg-gray-600 text-gray-300 cursor-not-allowed opacity-60'
  }`}
>
  <span>
    {startingTest
      ? 'Starting...'
      : !cameraGranted
      ? 'Allow Camera First'
      : !detectorReady
      ? 'Loading Face Detector...'
      : 'Begin Assessment Now'}
  </span>
  <ArrowRight className="w-4 h-4" />
</button>
          </div>
        </motion.div>
      </div>
    );
  }

  // ACTIVE TEST VIEW
  const currentQ = questions[currentIndex] || {};
  const answeredCount = Object.keys(answers).length;
  const isTimeCritical = timeLeft < 180; // less than 3 minutes

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Top Floating Header with Timer & Progress */}
      <div className="glass-card p-4 mb-6 border border-white/10 flex flex-wrap items-center justify-between gap-4 sticky top-20 z-20 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <span className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <BrainCircuit className="w-5 h-5" />
          </span>
          <div>
            <h2 className="text-base font-bold text-white leading-tight">{assessment?.title}</h2>
            <p className="text-xs text-slate-400">
              Question <span className="text-cyan-400 font-semibold">{currentIndex + 1}</span> of {questions.length} • {answeredCount} Answered
            </p>
          </div>
        </div>

        {/* Live Timer */}
        <div className={`flex items-center gap-2.5 px-4 py-2 rounded-xl border transition-all ${
          isTimeCritical 
            ? 'bg-rose-500/20 border-rose-500/50 text-rose-300 animate-pulse' 
            : 'bg-white/5 border-white/10 text-cyan-300'
        }`}>
          <Clock className="w-4 h-4" />
          <span className="font-mono font-bold text-sm tracking-wider">{formatTime(timeLeft)}</span>
          {isTimeCritical && <span className="text-[10px] font-bold uppercase text-rose-400">Ending Soon!</span>}
        </div>
{/* Live Face Detection Status */}
<div className={`flex items-center gap-2 px-4 py-2 rounded-xl border ${
  facePresent
    ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-400'
    : 'bg-rose-500/10 border-rose-500/40 text-rose-400'
}`}>
  <span className={`w-2 h-2 rounded-full ${
    facePresent ? 'bg-emerald-400' : 'bg-rose-400 animate-pulse'
  }`} />
  <span className="text-xs font-bold">
    {faceCount === 1 ? 'One Face Detected' : faceCount > 1 ? `${faceCount} Faces Detected` : 'Face Not Detected'}
  </span>
</div>
<div className={`flex items-center gap-2 px-4 py-2 rounded-xl border ${
  phoneDetected
    ? 'bg-rose-500/10 border-rose-500/40 text-rose-400'
    : 'bg-white/5 border-white/10 text-slate-300'
}`}>
  <span className={`w-2 h-2 rounded-full ${phoneDetected ? 'bg-rose-400 animate-pulse' : 'bg-emerald-400'}`} />
  <span className="text-xs font-bold">{phoneDetected ? 'Phone Detected' : objectDetectorReady ? 'Phone Scan Active' : 'Phone Scan Unavailable'}</span>
</div>

{/* Live Strikes Counter Badge */}
<div className={`flex items-center gap-1.5 px-3 py-2 rounded-xl border ${
  violationCount === 0
    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
    : violationCount === 1
    ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
    : 'bg-rose-500/15 border-rose-500/50 text-rose-300 animate-pulse'
}`}>
  <ShieldAlert className="w-3.5 h-3.5" />
  <span className="text-xs font-bold">Strikes: {violationCount} / 3</span>
</div>

        {/* Action Button */}
        <button
          onClick={() => setShowConfirmModal(true)}
          className="px-5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-bold text-xs transition-all flex items-center gap-1.5 shadow-lg shadow-cyan-500/20"
        >
          <Send className="w-3.5 h-3.5" />
          <span>Finish & Submit</span>
        </button>
      </div>

      {/* Immediate Visual Warning Banner Alert */}
      <AnimatePresence>
        {immediateAlert && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.98 }}
            className={`p-4 mb-6 rounded-2xl border flex items-center gap-3.5 shadow-xl ${
              immediateAlert.type === 'danger'
                ? 'bg-rose-950/80 border-rose-500/60 text-rose-200'
                : 'bg-amber-950/80 border-amber-500/60 text-amber-200'
            }`}
          >
            <div className={`p-2.5 rounded-xl ${
              immediateAlert.type === 'danger' ? 'bg-rose-500/20 text-rose-400' : 'bg-amber-500/20 text-amber-400'
            }`}>
              <ShieldAlert className="w-6 h-6 animate-pulse" />
            </div>
            <div className="flex-1">
              <h4 className="text-sm font-extrabold uppercase tracking-wide flex items-center gap-2">
                <span>{immediateAlert.title}</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-black/40 border border-white/10 uppercase">
                  Immediate Proctoring Alert
                </span>
              </h4>
              <p className="text-xs mt-0.5 opacity-90">{immediateAlert.message}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main 2-Column Split Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Column: 20-Question Palette & Live Webcam Preview */}
        <div className="lg:col-span-1 order-2 lg:order-1 space-y-4">
          {/* Live Webcam Proctoring Box */}
          <div className="glass-card p-3 border border-white/10 rounded-2xl overflow-hidden relative shadow-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-bold text-slate-300 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                Webcam Monitor
              </span>
              <span className="text-[10px] uppercase font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                AI Proctoring
              </span>
            </div>

            <div className="relative rounded-xl overflow-hidden bg-black aspect-video flex items-center justify-center border border-white/10">
              <video
                ref={attachVideoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover transform scale-x-[-1]"
              />
              <div className="absolute bottom-1.5 left-1.5 right-1.5 flex items-center justify-between text-[10px] pointer-events-none">
                <span className={`px-2 py-0.5 rounded font-bold backdrop-blur-md ${
                  faceCount === 1
                    ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-500/40'
                    : faceCount === 0
                    ? 'bg-rose-950/90 text-rose-300 border border-rose-500/50 animate-pulse'
                    : 'bg-rose-950/90 text-rose-300 border border-rose-500/50 animate-pulse'
                }`}>
                  {faceCount === 1 ? '1 Face (OK)' : faceCount === 0 ? 'Face Absent' : `${faceCount} Faces!`}
                </span>

                {phoneDetected && (
                  <span className="px-2 py-0.5 rounded font-bold bg-rose-950/90 text-rose-300 border border-rose-500/50 animate-bounce">
                    Phone!
                  </span>
                )}
              </div>
            </div>

            <div className="mt-2.5 flex items-center justify-between text-[11px] text-slate-400">
              <span>Camera: <strong className="text-emerald-400 font-semibold">{cameraGranted ? 'Active' : 'Offline'}</strong></span>
              <span>Strikes: <strong className={violationCount > 0 ? 'text-rose-400 font-semibold' : 'text-slate-300 font-semibold'}>{violationCount}/3</strong></span>
            </div>
          </div>

          <div className="glass-card p-5 border border-white/10 sticky top-44">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center justify-between">
              <span>Question Palette</span>
              <span className="text-cyan-400">{answeredCount}/20</span>
            </h4>

            {/* 4x5 Grid for 20 questions */}
            <div className="grid grid-cols-5 gap-2">
              {questions.map((q, idx) => {
                const isAnswered = answers[q.question_id] !== undefined;
                const isCurrent = idx === currentIndex;

                return (
                  <button
                    key={q.question_id || idx}
                    onClick={() => setCurrentIndex(idx)}
                    className={`h-9 rounded-lg font-bold text-xs transition-all flex items-center justify-center border ${
                      isCurrent
                        ? 'border-cyan-400 bg-cyan-500/20 text-cyan-300 ring-2 ring-cyan-500/30'
                        : isAnswered
                        ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-400'
                        : 'border-white/10 bg-white/5 text-slate-400 hover:border-white/30'
                    }`}
                  >
                    {idx + 1}
                  </button>
                );
              })}
            </div>

            {/* Legend */}
            <div className="mt-6 pt-4 border-t border-white/10 space-y-2 text-[11px] text-slate-400">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded bg-emerald-500/20 border border-emerald-500/40" />
                <span>Answered ({answeredCount})</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded bg-white/5 border border-white/10" />
                <span>Unanswered ({questions.length - answeredCount})</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded bg-cyan-500/20 border border-cyan-400" />
                <span>Current Question</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Question Content & Options */}
        <div className="lg:col-span-3 order-1 lg:order-2">
          <motion.div
            key={currentQ.question_id || currentIndex}
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.2 }}
            className="glass-card p-6 md:p-8 border border-white/10 relative"
          >
            {/* Question Badges */}
            <div className="flex items-center gap-2 mb-4 flex-wrap">
              <span className="px-2.5 py-1 rounded-md bg-white/10 text-slate-300 text-xs font-semibold">
                Question {currentIndex + 1} of {questions.length}
              </span>
              <span className="px-2.5 py-1 rounded-md bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold uppercase">
                {currentQ.skill_category}
              </span>
              <span className={`px-2.5 py-1 rounded-md text-xs font-semibold uppercase ${
                currentQ.difficulty === 'beginner' ? 'bg-cyan-500/10 text-cyan-300' :
                currentQ.difficulty === 'intermediate' ? 'bg-purple-500/10 text-purple-300' :
                'bg-amber-500/10 text-amber-300'
              }`}>
                {currentQ.difficulty}
              </span>
            </div>

            {/* Question Text */}
            <h3 className="text-lg md:text-xl font-bold text-white mb-6 leading-relaxed">
              {currentQ.question_text}
            </h3>

            {/* 4 MCQ Options */}
            <div className="space-y-3 mb-8">
              {(currentQ.options || []).map((option, optIdx) => {
                const optLetter = String.fromCharCode(65 + optIdx); // A, B, C, D
                const isSelected = answers[currentQ.question_id] === option;

                return (
                  <button
                    key={optIdx}
                    onClick={() => handleSelectOption(currentQ.question_id, option)}
                    className={`w-full text-left p-4 rounded-xl border transition-all flex items-start gap-4 ${
                      isSelected
                        ? 'border-cyan-400 bg-cyan-500/15 text-white ring-1 ring-cyan-500/50 shadow-lg shadow-cyan-500/10'
                        : 'border-white/10 bg-white/5 text-slate-300 hover:border-white/20 hover:bg-white/10'
                    }`}
                  >
                    <span className={`w-7 h-7 rounded-lg flex items-center justify-center font-mono font-bold text-xs shrink-0 transition-colors ${
                      isSelected ? 'bg-cyan-500 text-black' : 'bg-white/10 text-slate-400'
                    }`}>
                      {optLetter}
                    </span>
                    <span className="text-sm font-medium pt-0.5 leading-snug">{option}</span>
                  </button>
                );
              })}
            </div>

            {/* Bottom Navigation Buttons */}
            <div className="flex items-center justify-between pt-6 border-t border-white/10">
              <button
                disabled={currentIndex === 0}
                onClick={() => setCurrentIndex((prev) => Math.max(0, prev - 1))}
                className="px-5 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 text-xs font-semibold transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Previous</span>
              </button>

              <div className="flex items-center gap-3">
                {currentIndex < questions.length - 1 ? (
                  <button
                    onClick={() => setCurrentIndex((prev) => Math.min(questions.length - 1, prev + 1))}
                    className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-black font-bold text-xs transition-all flex items-center gap-2 shadow-lg shadow-cyan-500/20"
                  >
                    <span>Next Question</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                ) : (
                  <button
                    onClick={() => setShowConfirmModal(true)}
                    className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-black font-bold text-xs transition-all flex items-center gap-2 shadow-lg shadow-emerald-500/20"
                  >
                    <span>Review & Submit</span>
                    <Send className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Proctoring Warning Modal (1st and 2nd violation) */}
      <AnimatePresence>
        {showProctoringWarning && (
          <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="glass-card max-w-md w-full p-7 border border-amber-500/40 shadow-2xl"
            >
              <div className="w-14 h-14 rounded-full bg-amber-500/15 border border-amber-500/30 flex items-center justify-center mx-auto mb-4">
                <ShieldAlert className="w-7 h-7 text-amber-400" />
              </div>
              <h3 className="text-xl font-extrabold text-amber-300 text-center mb-2">
                {proctoringWarningLevel === 1 ? 'Proctoring Warning 1/3' : 'Final Warning 2/3'}
              </h3>
              <p className="text-sm text-slate-300 text-center mb-4">
                {proctoringWarningLevel === 1
                  ? 'A proctoring violation has been recorded. Please follow the assessment rules. Two more recorded violations may terminate your assessment.'
                  : 'A second proctoring violation has been recorded. One more recorded violation will terminate your assessment.'}
              </p>
              <div className="p-3 rounded-xl bg-white/5 border border-white/10 text-xs text-slate-300 mb-5">
                <span className="font-semibold text-white">Detected activity: </span>
                {proctoringWarningDetails}
              </div>
              <div className="text-center text-xs text-amber-300 mb-5">
                {proctoringWarningLevel === 1
                  ? '2 warnings remaining before termination.'
                  : 'This is your final warning.'}
              </div>
              <button
                onClick={() => setShowProctoringWarning(false)}
                className="w-full px-5 py-3 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 text-black font-bold text-sm hover:brightness-110 transition-all"
              >
                I Understand — Continue Assessment
              </button>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Confirmation Modal */}
      <AnimatePresence>
        {showConfirmModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="glass-card p-6 max-w-md w-full border border-white/10 shadow-2xl"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                  <AlertCircle className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Submit Assessment?</h3>
                  <p className="text-xs text-slate-400">Final evaluation confirmation</p>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-2 mb-6 text-xs text-slate-300">
                <div className="flex justify-between">
                  <span>Total Questions:</span>
                  <span className="font-bold text-white">{questions.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Questions Answered:</span>
                  <span className="font-bold text-emerald-400">{answeredCount}</span>
                </div>
                <div className="flex justify-between">
                  <span>Unanswered:</span>
                  <span className="font-bold text-rose-400">{questions.length - answeredCount}</span>
                </div>
                <div className="flex justify-between">
                  <span>Time Remaining:</span>
                  <span className="font-mono text-cyan-300">{formatTime(timeLeft)}</span>
                </div>
              </div>

              <p className="text-xs text-slate-400 mb-6 leading-relaxed">
                Once submitted, answers will be locked, graded immediately out of 20, and results forwarded to the hiring team.
              </p>

              <div className="flex items-center justify-end gap-3">
                <button
                  disabled={isSubmitting}
                  onClick={() => setShowConfirmModal(false)}
                  className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-slate-300 text-xs font-semibold transition-colors"
                >
                  Continue Test
                </button>
                <button
                  disabled={isSubmitting}
                  onClick={handleSubmitAnswers}
                  className="px-6 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-black font-bold text-xs transition-all shadow-lg shadow-cyan-500/20 flex items-center gap-1.5"
                >
                  {isSubmitting ? (
                    <>
                      <div className="w-3.5 h-3.5 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                      <span>Grading...</span>
                    </>
                  ) : (
                    <>
                      <Send className="w-3.5 h-3.5" />
                      <span>Confirm & Submit</span>
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
