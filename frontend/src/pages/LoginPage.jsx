import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { authAPI } from '../services/api';
import { 
  Sparkles, 
  ArrowRight, 
  Loader2, 
  Lock, 
  Mail, 
  UserCheck, 
  Briefcase, 
  ShieldCheck,
  X,
  KeyRound,
  CheckCircle2,
  RefreshCw,
  Eye,
  EyeOff,
  ShieldAlert,
  ArrowLeft
} from 'lucide-react';

export default function LoginPage() {
  const { login } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();

  // Login form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Forgot Password Modal State
  const [forgotModalOpen, setForgotModalOpen] = useState(false);
  const [forgotStep, setForgotStep] = useState('EMAIL'); // 'EMAIL' | 'OTP' | 'NEW_PASS' | 'SUCCESS'
  const [forgotEmail, setForgotEmail] = useState('');
  const [forgotOtp, setForgotOtp] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [forgotLoading, setForgotLoading] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [attemptsRemaining, setAttemptsRemaining] = useState(5);

  // Cooldown timer for OTP Resend
  useEffect(() => {
    let timer;
    if (resendCooldown > 0) {
      timer = setInterval(() => {
        setResendCooldown((prev) => (prev > 0 ? prev - 1 : 0));
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [resendCooldown]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      showToast('Please fill in both email and password.', 'warning');
      return;
    }

    setLoading(true);
    try {
      const user = await login(email, password);
      showToast(`Welcome back, ${user.name}!`, 'success');
      
      // Navigate to role appropriate dashboard
      if (user.role === 'recruiter') {
        navigate('/recruiter');
      } else if (user.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      console.error('Login error:', err);
      const detail = err.response?.data?.detail || 'Invalid email or password.';
      showToast(detail, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (demoEmail, demoPassword) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
  };

  // --------------------------------------------------------------------------
  // FORGOT PASSWORD STEP 1: REQUEST OTP
  // --------------------------------------------------------------------------
  const handleRequestOtp = async (e) => {
    e.preventDefault();
    const cleanEmail = forgotEmail.trim().toLowerCase();
    if (!cleanEmail) {
      showToast('Please enter your registered email address.', 'warning');
      return;
    }

    setForgotLoading(true);
    try {
      const res = await authAPI.forgotPassword(cleanEmail);
      showToast(res.data.message || 'OTP verification code sent to your email.', 'success');
      setForgotStep('OTP');
      setResendCooldown(60);
      setAttemptsRemaining(5);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to send reset code. Please try again.';
      showToast(msg, 'error');
    } finally {
      setForgotLoading(false);
    }
  };

  // --------------------------------------------------------------------------
  // FORGOT PASSWORD STEP 2: VERIFY OTP
  // --------------------------------------------------------------------------
  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    const cleanOtp = forgotOtp.trim();
    if (!cleanOtp) {
      showToast('Please enter the 6-digit OTP code.', 'warning');
      return;
    }

    setForgotLoading(true);
    try {
      const res = await authAPI.verifyOTP(forgotEmail.trim().toLowerCase(), cleanOtp);
      showToast(res.data.message || 'OTP verified successfully.', 'success');
      setResetToken(res.data.reset_token);
      setForgotStep('NEW_PASS');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Invalid or expired OTP.';
      showToast(msg, 'error');
      setAttemptsRemaining((prev) => Math.max(0, prev - 1));
    } finally {
      setForgotLoading(false);
    }
  };

  // --------------------------------------------------------------------------
  // FORGOT PASSWORD STEP 3: RESEND OTP
  // --------------------------------------------------------------------------
  const handleResendOtp = async () => {
    if (resendCooldown > 0 || forgotLoading) return;

    setForgotLoading(true);
    try {
      const res = await authAPI.resendOTP(forgotEmail.trim().toLowerCase());
      showToast(res.data.message || 'A fresh OTP code has been dispatched.', 'success');
      setResendCooldown(60);
      setAttemptsRemaining(5);
      setForgotOtp('');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Unable to resend OTP at this time.';
      showToast(msg, 'error');
    } finally {
      setForgotLoading(false);
    }
  };

  // --------------------------------------------------------------------------
  // FORGOT PASSWORD STEP 4: SUBMIT NEW PASSWORD
  // --------------------------------------------------------------------------
  const handleResetPassword = async (e) => {
    e.preventDefault();
    if (newPassword.length < 6) {
      showToast('New password must be at least 6 characters.', 'warning');
      return;
    }
    if (newPassword !== confirmPassword) {
      showToast('Passwords do not match. Please re-check.', 'warning');
      return;
    }

    setForgotLoading(true);
    try {
      const res = await authAPI.resetPassword(
        forgotEmail.trim().toLowerCase(),
        resetToken,
        newPassword
      );
      showToast(res.data.message || 'Password reset successfully!', 'success');
      setForgotStep('SUCCESS');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to update password. Session may have expired.';
      showToast(msg, 'error');
    } finally {
      setForgotLoading(false);
    }
  };

  const closeForgotModal = () => {
    setForgotModalOpen(false);
    setForgotStep('EMAIL');
    setForgotOtp('');
    setResetToken('');
    setNewPassword('');
    setConfirmPassword('');
  };

  const handleFinishSuccess = () => {
    setEmail(forgotEmail);
    setPassword('');
    closeForgotModal();
    showToast('You can now log in with your new password.', 'info');
  };

  return (
    <div className="min-h-screen bg-dark-900 flex items-center justify-center p-4 relative overflow-hidden">
      
      {/* Background Neon Orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-[120px] pointer-events-none" />

      <div className="w-full max-w-4xl grid grid-cols-1 lg:grid-cols-12 rounded-3xl glass-panel border border-white/20 shadow-2xl shadow-cyan-950/40 overflow-hidden relative z-10">
        
        {/* Left Side: Brand Visual Info */}
        <div className="lg:col-span-5 p-8 md:p-10 bg-gradient-to-br from-cyan-950/40 via-dark-850 to-purple-950/40 border-b lg:border-b-0 lg:border-r border-white/10 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-8">
              <div className="w-9 h-9 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-cyan-400" />
              </div>
              <span className="font-heading font-extrabold text-xl text-white">
                Skill<span className="text-cyan-400">Sphere</span>
              </span>
            </div>

            <h2 className="text-2xl font-bold font-heading text-white mb-3">
              Career & Job Intelligence Portal
            </h2>
            <p className="text-xs text-slate-400 leading-relaxed mb-6">
              Sign in to manage resume OCR parses, evaluate explainable role match scores, or manage candidate ATS pipelines.
            </p>

            {/* Demo Quick Logins */}
            <div className="space-y-3">
              <p className="text-[11px] uppercase tracking-wider font-semibold text-cyan-400">
                1-Click Evaluator Demo Accounts:
              </p>
              
              <button
                type="button"
                onClick={() => handleQuickLogin('candidate@skillsphere.com', 'password123')}
                className="w-full text-left p-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs text-slate-300 hover:text-white flex items-center justify-between transition-colors"
              >
                <span className="flex items-center gap-2">
                  <UserCheck className="w-4 h-4 text-cyan-400" />
                  <span>Job Seeker: <strong>Alex Rivera</strong></span>
                </span>
                <span className="text-[10px] text-cyan-300 font-mono">Fill</span>
              </button>

              <button
                type="button"
                onClick={() => handleQuickLogin('recruiter@skillsphere.com', 'password123')}
                className="w-full text-left p-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs text-slate-300 hover:text-white flex items-center justify-between transition-colors"
              >
                <span className="flex items-center gap-2">
                  <Briefcase className="w-4 h-4 text-purple-400" />
                  <span>Recruiter: <strong>Sarah Jenkins</strong></span>
                </span>
                <span className="text-[10px] text-purple-300 font-mono">Fill</span>
              </button>

              <button
                type="button"
                onClick={() => handleQuickLogin('admin@skillsphere.com', 'password123')}
                className="w-full text-left p-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs text-slate-300 hover:text-white flex items-center justify-between transition-colors"
              >
                <span className="flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span>Admin: <strong>Elena Rostova</strong></span>
                </span>
                <span className="text-[10px] text-emerald-300 font-mono">Fill</span>
              </button>
            </div>
          </div>

          <div className="pt-6 text-[11px] text-slate-500">
            Protected by bcrypt hashing & JWT stateless authentication. Real email dispatch active.
          </div>
        </div>

        {/* Right Side: Form */}
        <div className="lg:col-span-7 p-8 md:p-12 flex flex-col justify-center">
          <div className="mb-6">
            <h3 className="text-2xl font-bold font-heading text-white">Sign In</h3>
            <p className="text-xs text-slate-400 mt-1">Enter your credentials to access your portal session</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Email Address</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  className="w-full pl-10 pr-4 py-2.5 text-sm rounded-xl glass-input"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-medium text-slate-300">Password</label>
                <button
                  type="button"
                  onClick={() => {
                    setForgotEmail(email);
                    setForgotStep('EMAIL');
                    setForgotModalOpen(true);
                  }}
                  className="text-xs text-cyan-400 hover:text-cyan-300 font-medium transition-colors hover:underline"
                >
                  Forgot Password?
                </button>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-10 py-2.5 text-sm rounded-xl glass-input"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200 transition-colors"
                  aria-label="Toggle password visibility"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-3 rounded-xl text-sm font-bold bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-lg shadow-cyan-500/25 hover:brightness-110 flex items-center justify-center gap-2 transition-all"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
              Sign In to SkillSphere
            </button>
          </form>

          <p className="text-center text-xs text-slate-400 mt-6">
            Don't have an account yet?{' '}
            <Link to="/register" className="text-cyan-400 hover:text-cyan-300 font-semibold underline">
              Create an account
            </Link>
          </p>
        </div>

      </div>

      {/* ====================================================================== */}
      {/* MODERN FORGOT PASSWORD / PASSWORD RECOVERY MODAL */}
      {/* ====================================================================== */}
      <AnimatePresence>
        {forgotModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ duration: 0.2 }}
              className="w-full max-w-md rounded-3xl glass-panel border border-cyan-500/30 p-6 md:p-8 shadow-2xl shadow-cyan-950/60 relative overflow-hidden bg-dark-900/95"
            >
              {/* Glowing header accent line */}
              <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-cyan-400 via-indigo-500 to-purple-500" />

              {/* Close Button */}
              <button
                onClick={closeForgotModal}
                className="absolute top-5 right-5 p-1.5 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                aria-label="Close recovery modal"
              >
                <X className="w-5 h-5" />
              </button>

              {/* Header Title */}
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-2xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400">
                  <KeyRound className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold font-heading text-white">
                    Password Recovery
                  </h3>
                  <p className="text-[11px] text-slate-400">
                    Secure OTP account verification
                  </p>
                </div>
              </div>

              {/* -------------------------------------------------------------- */}
              {/* STEP 1: ENTER REGISTERED EMAIL */}
              {/* -------------------------------------------------------------- */}
              {forgotStep === 'EMAIL' && (
                <form onSubmit={handleRequestOtp} className="space-y-4">
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Enter your registered email address and we will dispatch a secure 6-digit verification code to your inbox.
                  </p>

                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1.5">Registered Email</label>
                    <div className="relative">
                      <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                      <input
                        type="email"
                        required
                        value={forgotEmail}
                        onChange={(e) => setForgotEmail(e.target.value)}
                        placeholder="your.email@example.com"
                        className="w-full pl-10 pr-4 py-2.5 text-sm rounded-xl glass-input"
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={forgotLoading}
                    className="w-full py-2.5 rounded-xl text-sm font-bold bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-lg shadow-cyan-500/20 hover:brightness-110 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                  >
                    {forgotLoading ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Sending Code...</span>
                      </>
                    ) : (
                      <>
                        <span>Send 6-Digit Code</span>
                        <ArrowRight className="w-4 h-4" />
                      </>
                    )}
                  </button>

                  <div className="text-center pt-2">
                    <button
                      type="button"
                      onClick={closeForgotModal}
                      className="text-xs text-slate-400 hover:text-white transition-colors"
                    >
                      Return to Sign In
                    </button>
                  </div>
                </form>
              )}

              {/* -------------------------------------------------------------- */}
              {/* STEP 2: ENTER OTP */}
              {/* -------------------------------------------------------------- */}
              {forgotStep === 'OTP' && (
                <form onSubmit={handleVerifyOtp} className="space-y-4">
                  <div className="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-xs text-cyan-200 flex items-start gap-2">
                    <Mail className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                    <span>
                      We sent a 6-digit OTP to <strong>{forgotEmail}</strong>. Valid for 15 minutes.
                    </span>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1.5">
                      6-Digit Verification Code
                    </label>
                    <input
                      type="text"
                      maxLength={6}
                      required
                      value={forgotOtp}
                      onChange={(e) => setForgotOtp(e.target.value.replace(/\D/g, ''))}
                      placeholder="123456"
                      className="w-full py-3 text-center text-xl font-mono tracking-[10px] rounded-xl glass-input font-bold text-cyan-300 placeholder-slate-600"
                    />
                    <div className="flex items-center justify-between mt-1 text-[11px] text-slate-400">
                      <span>{attemptsRemaining} attempts remaining</span>
                      {resendCooldown > 0 ? (
                        <span className="text-slate-500">Resend in {resendCooldown}s</span>
                      ) : (
                        <button
                          type="button"
                          onClick={handleResendOtp}
                          disabled={forgotLoading}
                          className="text-cyan-400 hover:text-cyan-300 font-semibold underline disabled:opacity-50"
                        >
                          Resend Code
                        </button>
                      )}
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={forgotLoading || forgotOtp.length < 6}
                    className="w-full py-2.5 rounded-xl text-sm font-bold bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-lg shadow-cyan-500/20 hover:brightness-110 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                  >
                    {forgotLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      'Verify & Proceed'
                    )}
                  </button>

                  <div className="flex items-center justify-between pt-2 text-xs">
                    <button
                      type="button"
                      onClick={() => setForgotStep('EMAIL')}
                      className="text-slate-400 hover:text-white flex items-center gap-1 transition-colors"
                    >
                      <ArrowLeft className="w-3.5 h-3.5" />
                      Change Email
                    </button>
                    <button
                      type="button"
                      onClick={closeForgotModal}
                      className="text-slate-400 hover:text-white transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              )}

              {/* -------------------------------------------------------------- */}
              {/* STEP 3: ENTER NEW PASSWORD */}
              {/* -------------------------------------------------------------- */}
              {forgotStep === 'NEW_PASS' && (
                <form onSubmit={handleResetPassword} className="space-y-4">
                  <p className="text-xs text-slate-300">
                    OTP verified! Set your new password below (minimum 6 characters).
                  </p>

                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1.5">New Password</label>
                    <div className="relative">
                      <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                      <input
                        type={showNewPassword ? 'text' : 'password'}
                        required
                        minLength={6}
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        placeholder="••••••••"
                        className="w-full pl-10 pr-10 py-2.5 text-sm rounded-xl glass-input"
                      />
                      <button
                        type="button"
                        onClick={() => setShowNewPassword(!showNewPassword)}
                        className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                      >
                        {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1.5">Confirm New Password</label>
                    <div className="relative">
                      <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                      <input
                        type={showConfirmPassword ? 'text' : 'password'}
                        required
                        minLength={6}
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="••••••••"
                        className="w-full pl-10 pr-10 py-2.5 text-sm rounded-xl glass-input"
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                      >
                        {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                    {confirmPassword && newPassword !== confirmPassword && (
                      <p className="text-[11px] text-rose-400 mt-1">Passwords do not match.</p>
                    )}
                    {confirmPassword && newPassword === confirmPassword && (
                      <p className="text-[11px] text-emerald-400 mt-1">✓ Passwords match.</p>
                    )}
                  </div>

                  <button
                    type="submit"
                    disabled={forgotLoading || newPassword.length < 6 || newPassword !== confirmPassword}
                    className="w-full py-2.5 rounded-xl text-sm font-bold bg-gradient-to-r from-emerald-500 to-cyan-600 text-white shadow-lg shadow-emerald-500/20 hover:brightness-110 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                  >
                    {forgotLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      'Update Password & Complete'
                    )}
                  </button>
                </form>
              )}

              {/* -------------------------------------------------------------- */}
              {/* STEP 4: SUCCESS CONFIRMATION */}
              {/* -------------------------------------------------------------- */}
              {forgotStep === 'SUCCESS' && (
                <div className="text-center py-4 space-y-4">
                  <div className="w-16 h-16 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 flex items-center justify-center mx-auto shadow-lg shadow-emerald-500/20">
                    <CheckCircle2 className="w-8 h-8" />
                  </div>
                  <div>
                    <h4 className="text-base font-bold text-white mb-1">
                      Password Successfully Updated!
                    </h4>
                    <p className="text-xs text-slate-300 leading-relaxed max-w-xs mx-auto">
                      Your SkillSphere password has been securely updated and a confirmation email has been dispatched.
                    </p>
                  </div>
                  <button
                    onClick={handleFinishSuccess}
                    className="w-full py-3 rounded-xl text-sm font-bold bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-lg shadow-cyan-500/25 hover:brightness-110 transition-all"
                  >
                    Sign In with New Password
                  </button>
                </div>
              )}

            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div>
  );
}
