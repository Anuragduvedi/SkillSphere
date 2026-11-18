import React, { useState, useEffect } from 'react';
import {
  BrainCircuit,
  Plus,
  Edit3,
  Trash2,
  CheckCircle2,
  XCircle,
  Clock,
  Search,
  Filter,
  Eye,
  Send,
  Layers,
  FileText,
  Sparkles,
  Download,
  AlertTriangle,
  Award,
  RefreshCw,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Briefcase,
  Building2,
  Check,
  X,
  Share2,
  Copy,
  Users,
  Calendar,
  ShieldAlert,
  ExternalLink,
  CheckSquare,
  Square,
  Mail
} from 'lucide-react';
import { assessmentAPI, jobsAPI } from '../services/api';
import { useToast } from '../context/ToastContext';
import RadialGauge from './RadialGauge';

const TECHNOLOGIES = [
  'All',
  'Python',
  'Java',
  'React',
  'Fullstack MERN',
  'JavaScript',
  'SQL',
  'HTML & CSS',
  'Cloud DevOps'
];

const DIFFICULTIES = ['All', 'beginner', 'intermediate', 'advanced'];

export default function RecruiterAssessmentManager() {
  const { showToast } = useToast();

  const [activeTab, setActiveTab] = useState('questions'); 
  // 'questions', 'create', 'published', 'drafts', 'results', 'stats'

  // Data states
  const [jobs, setJobs] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [candidateResults, setCandidateResults] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  // Recruiter Direct Candidate Assignment States
  const [assignableCandidates, setAssignableCandidates] = useState([]);
  const [assignedTracking, setAssignedTracking] = useState([]);
  const [selectedCandidateIds, setSelectedCandidateIds] = useState([]);
  const [candidateSearch, setCandidateSearch] = useState('');
  const [candidateJobFilter, setCandidateJobFilter] = useState('');
  const [assignSource, setAssignSource] = useState('template'); // 'template' or 'custom'
  const [assignJobId, setAssignJobId] = useState('');
  const [assignTemplateId, setAssignTemplateId] = useState('');
  const [assignTitle, setAssignTitle] = useState('');
  const [assignDescription, setAssignDescription] = useState('');
  const [assignTech, setAssignTech] = useState('Python');
  const [assignDuration, setAssignDuration] = useState(25);
  const [assignPassPercent, setAssignPassPercent] = useState(60.0);
  const [assignExpiresDays, setAssignExpiresDays] = useState(7);
  const [assignSendEmail, setAssignSendEmail] = useState(true);
  const [assigning, setAssigning] = useState(false);
  const [recentAssignments, setRecentAssignments] = useState([]);
  const [copiedToken, setCopiedToken] = useState(null);

  // Tracking Filter States
  const [trackingSearch, setTrackingSearch] = useState('');
  const [trackingStatusFilter, setTrackingStatusFilter] = useState('all');
  const [trackingJobFilter, setTrackingJobFilter] = useState('');

  // AI Question Generation States
  const [isAIQuestionModalOpen, setIsAIQuestionModalOpen] = useState(false);
  const [aiRole, setAiRole] = useState('Senior Full Stack Developer');
  const [aiTech, setAiTech] = useState('Python');
  const [aiCount, setAiCount] = useState(5);
  const [aiDiff, setAiDiff] = useState('intermediate');
  const [aiGenerating, setAiGenerating] = useState(false);
  const [aiGeneratedQuestions, setAiGeneratedQuestions] = useState([]);

  // Filters for Questions tab
  const [techFilter, setTechFilter] = useState('All');
  const [diffFilter, setDiffFilter] = useState('All');
  const [jobFilter, setJobFilter] = useState('');
  const [questionSearch, setQuestionSearch] = useState('');

  // Modals
  const [isCreateQuestionOpen, setIsCreateQuestionOpen] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState(null);
  const [isImportLibraryOpen, setIsImportLibraryOpen] = useState(false);
  const [previewTemplate, setPreviewTemplate] = useState(null);
  const [inspectResultId, setInspectResultId] = useState(null);
  const [inspectResultData, setInspectResultData] = useState(null);

  // Form State: Create / Edit Question
  const [qTech, setQTech] = useState('Python');
  const [qDiff, setQDiff] = useState('intermediate');
  const [qJobId, setQJobId] = useState('');
  const [qText, setQText] = useState('');
  const [qOptA, setQOptA] = useState('');
  const [qOptB, setQOptB] = useState('');
  const [qOptC, setQOptC] = useState('');
  const [qOptD, setQOptD] = useState('');
  const [qCorrect, setQCorrect] = useState('A');
  const [qExplanation, setQExplanation] = useState('');
  const [savingQuestion, setSavingQuestion] = useState(false);

  // Form State: Create / Edit Assessment Template
  const [assessmentJobId, setAssessmentJobId] = useState('');
  const [assessmentTitle, setAssessmentTitle] = useState('');
  const [assessmentTech, setAssessmentTech] = useState('');
  const [assessmentDuration, setAssessmentDuration] = useState(25);
  const [assessmentPassPercent, setAssessmentPassPercent] = useState(60.0);
  const [selectedQuestionIds, setSelectedQuestionIds] = useState([]);
  const [savingAssessment, setSavingAssessment] = useState(false);
  const [editingTemplateId, setEditingTemplateId] = useState(null);

  // Import Library State
  const [importTech, setImportTech] = useState('Python');
  const [importCount, setImportCount] = useState(20);
  const [importing, setImporting] = useState(false);

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [jobsRes, questionsRes, templatesRes, resultsRes, statsRes, assignableRes, trackingRes] = await Promise.all([
        jobsAPI.list(),
        assessmentAPI.getQuestions(),
        assessmentAPI.getTemplates(),
        assessmentAPI.getRecruiterCandidateResults(),
        assessmentAPI.getRecruiterStats(),
        assessmentAPI.getAssignableCandidates(),
        assessmentAPI.getAssignedTracking(),
      ]);

      const jobsList = jobsRes.data || [];
      const templatesList = templatesRes.data || [];
      const pubTemplates = templatesList.filter((t) => t.status === 'published');

      setJobs(jobsList);
      setQuestions(questionsRes.data || []);
      setTemplates(templatesList);
      setCandidateResults(resultsRes.data || []);
      setStats(statsRes.data || null);
      setAssignableCandidates(assignableRes.data || []);
      setAssignedTracking(trackingRes.data || []);

      if (jobsList.length > 0) {
        if (!assessmentJobId) {
          setAssessmentJobId(jobsList[0].job_id);
          setAssessmentTitle(`${jobsList[0].title} Technical Assessment`);
          setAssessmentTech(jobsList[0].skills?.[0] || 'Full Stack');
        }
        if (!assignJobId) {
          setAssignJobId(jobsList[0].job_id);
          setAssignTitle(`${jobsList[0].title} Technical Assessment`);
          setAssignTech(jobsList[0].skills?.[0] || 'Python');
        }
      }

      if (pubTemplates.length > 0 && !assignTemplateId) {
        setAssignTemplateId(pubTemplates[0].template_id);
      }
    } catch (err) {
      console.error('Error loading assessment management data:', err);
      showToast('Failed to load assessment manager data.', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Helper to refresh questions
  const refreshQuestions = async () => {
    try {
      const params = {};
      if (techFilter !== 'All') params.technology = techFilter;
      if (diffFilter !== 'All') params.difficulty = diffFilter;
      if (jobFilter) params.job_id = Number(jobFilter);
      if (questionSearch) params.search = questionSearch;

      const res = await assessmentAPI.getQuestions(params);
      setQuestions(res.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (!loading) {
      refreshQuestions();
    }
  }, [techFilter, diffFilter, jobFilter, questionSearch]);

  // ================= 1. QUESTION CRUD HANDLERS =================

  const handleOpenCreateQuestion = () => {
    setEditingQuestion(null);
    setQTech('Python');
    setQDiff('intermediate');
    setQJobId('');
    setQText('');
    setQOptA('');
    setQOptB('');
    setQOptC('');
    setQOptD('');
    setQCorrect('A');
    setQExplanation('');
    setIsCreateQuestionOpen(true);
  };

  const handleOpenEditQuestion = (q) => {
    setEditingQuestion(q);
    setQTech(q.technology || 'Python');
    setQDiff(q.difficulty || 'intermediate');
    setQJobId(q.job_id || '');
    setQText(q.question_text || '');
    const opts = q.options || [];
    setQOptA(opts[0] || '');
    setQOptB(opts[1] || '');
    setQOptC(opts[2] || '');
    setQOptD(opts[3] || '');

    if (q.correct_answer === opts[0]) setQCorrect('A');
    else if (q.correct_answer === opts[1]) setQCorrect('B');
    else if (q.correct_answer === opts[2]) setQCorrect('C');
    else if (q.correct_answer === opts[3]) setQCorrect('D');
    else setQCorrect('A');

    setQExplanation(q.explanation || '');
    setIsCreateQuestionOpen(true);
  };

  const handleSaveQuestion = async (e) => {
    e.preventDefault();
    const opts = [qOptA.trim(), qOptB.trim(), qOptC.trim(), qOptD.trim()];
    if (opts.some((o) => !o)) {
      showToast('Please provide all 4 MCQ options.', 'error');
      return;
    }

    let correctText = opts[0];
    if (qCorrect === 'B') correctText = opts[1];
    if (qCorrect === 'C') correctText = opts[2];
    if (qCorrect === 'D') correctText = opts[3];

    const payload = {
      technology: qTech,
      difficulty: qDiff,
      question_text: qText.trim(),
      options: opts,
      correct_answer: correctText,
      explanation: qExplanation.trim() || null,
      job_id: qJobId ? Number(qJobId) : null,
    };

    setSavingQuestion(true);
    try {
      if (editingQuestion) {
        await assessmentAPI.updateQuestion(editingQuestion.question_id, payload);
        showToast('Question updated successfully!', 'success');
      } else {
        await assessmentAPI.createQuestion(payload);
        showToast('New question created in your question bank!', 'success');
      }
      setIsCreateQuestionOpen(false);
      refreshQuestions();
      const statsRes = await assessmentAPI.getRecruiterStats();
      setStats(statsRes.data);
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to save question.', 'error');
    } finally {
      setSavingQuestion(false);
    }
  };

  const handleDeleteQuestion = async (questionId) => {
    if (!window.confirm('Are you sure you want to delete this technical question?')) return;
    try {
      await assessmentAPI.deleteQuestion(questionId);
      showToast('Question deleted.', 'info');
      refreshQuestions();
      const statsRes = await assessmentAPI.getRecruiterStats();
      setStats(statsRes.data);
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to delete question.', 'error');
    }
  };

  const handleImportFromLibrary = async () => {
    setImporting(true);
    try {
      const res = await assessmentAPI.importFromLibrary({
        technology: importTech,
        count: importCount,
      });
      showToast(res.data.message || 'Questions imported into your bank!', 'success');
      setIsImportLibraryOpen(false);
      refreshQuestions();
      const statsRes = await assessmentAPI.getRecruiterStats();
      setStats(statsRes.data);
    } catch (err) {
      showToast(err.response?.data?.detail || 'Import failed.', 'error');
    } finally {
      setImporting(false);
    }
  };

  // ================= 2. ASSESSMENT TEMPLATE HANDLERS =================

  const handleToggleSelectQuestion = (qId) => {
    setSelectedQuestionIds((prev) => {
      if (prev.includes(qId)) {
        return prev.filter((id) => id !== qId);
      } else {
        if (prev.length >= 20) {
          showToast('Maximum 20 questions reached for this assessment.', 'warning');
          return prev;
        }
        return [...prev, qId];
      }
    });
  };

  const handleSaveAssessment = async (publishStatus = 'draft') => {
    if (!assessmentJobId) {
      showToast('Please select a job opening.', 'error');
      return;
    }
    if (publishStatus === 'published' && selectedQuestionIds.length !== 20) {
      showToast(`Cannot publish: Exactly 20 questions required (currently ${selectedQuestionIds.length} selected).`, 'error');
      return;
    }

    const payload = {
      job_id: Number(assessmentJobId),
      title: assessmentTitle || 'Technical Assessment',
      tech_stack: assessmentTech || 'Full Stack',
      duration_minutes: Number(assessmentDuration),
      passing_percentage: Number(assessmentPassPercent),
      status: publishStatus,
      question_ids: selectedQuestionIds,
    };

    setSavingAssessment(true);
    try {
      if (editingTemplateId) {
        await assessmentAPI.updateTemplate(editingTemplateId, payload);
        showToast(
          publishStatus === 'published' 
            ? 'Assessment published successfully! Shortlisted candidates will receive this test.' 
            : 'Assessment draft saved.',
          'success'
        );
      } else {
        await assessmentAPI.createTemplate(payload);
        showToast(
          publishStatus === 'published'
            ? 'Assessment created and published!'
            : 'Assessment saved as draft.',
          'success'
        );
      }

      // Reset & Reload
      setEditingTemplateId(null);
      setSelectedQuestionIds([]);
      const [tRes, statsRes] = await Promise.all([
        assessmentAPI.getTemplates(),
        assessmentAPI.getRecruiterStats(),
      ]);
      setTemplates(tRes.data || []);
      setStats(statsRes.data);
      setActiveTab(publishStatus === 'published' ? 'published' : 'drafts');
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to save assessment.', 'error');
    } finally {
      setSavingAssessment(false);
    }
  };

  const handleEditDraft = (tmpl) => {
    setEditingTemplateId(tmpl.template_id);
    setAssessmentJobId(tmpl.job_id);
    setAssessmentTitle(tmpl.title);
    setAssessmentTech(tmpl.tech_stack);
    setAssessmentDuration(tmpl.duration_minutes || 25);
    setAssessmentPassPercent(tmpl.passing_percentage || 60);
    setSelectedQuestionIds(tmpl.question_ids || []);
    setActiveTab('create');
    showToast(`Loaded draft: ${tmpl.title}`, 'info');
  };

  const handlePublishTemplate = async (templateId) => {
    try {
      await assessmentAPI.publishTemplate(templateId);
      showToast('Assessment published! Shortlisted candidates will now receive this test.', 'success');
      const [tRes, statsRes] = await Promise.all([
        assessmentAPI.getTemplates(),
        assessmentAPI.getRecruiterStats(),
      ]);
      setTemplates(tRes.data || []);
      setStats(statsRes.data);
    } catch (err) {
      showToast(err.response?.data?.detail || 'Could not publish assessment.', 'error');
    }
  };

  const handleDeleteTemplate = async (templateId) => {
    if (!window.confirm('Are you sure you want to delete this assessment?')) return;
    try {
      await assessmentAPI.deleteTemplate(templateId);
      showToast('Assessment deleted.', 'info');
      const [tRes, statsRes] = await Promise.all([
        assessmentAPI.getTemplates(),
        assessmentAPI.getRecruiterStats(),
      ]);
      setTemplates(tRes.data || []);
      setStats(statsRes.data);
    } catch (err) {
      showToast('Failed to delete template.', 'error');
    }
  };

  const handleInspectResults = async (assessmentId) => {
    setInspectResultId(assessmentId);
    try {
      const res = await assessmentAPI.getResults(assessmentId);
      setInspectResultData(res.data);
    } catch (err) {
      showToast('Could not load candidate result details.', 'error');
    }
  };

  const handleOpenPreview = async (tmpl) => {
    try {
      const res = await assessmentAPI.getTemplateDetails(tmpl.template_id);
      setPreviewTemplate(res.data);
    } catch (err) {
      showToast('Could not load preview details.', 'error');
    }
  };

  // Link Copying with Visual Feedback
  const handleCopyLink = async (token) => {
    const url = `${window.location.origin}/assessment/${token}`;
    try {
      await navigator.clipboard.writeText(url);
      setCopiedToken(token);
      showToast('Assessment URL copied to clipboard!', 'success');
      setTimeout(() => setCopiedToken(null), 2500);
    } catch (err) {
      // Fallback for clipboard
      const input = document.createElement('textarea');
      input.value = url;
      document.body.appendChild(input);
      input.select();
      document.execCommand('copy');
      document.body.removeChild(input);
      setCopiedToken(token);
      showToast('Assessment URL copied to clipboard!', 'success');
      setTimeout(() => setCopiedToken(null), 2500);
    }
  };

  // Native Browser Sharing with Fallback to Clipboard
  const handleShareLink = async (item) => {
    const url = `${window.location.origin}/assessment/${item.test_token}`;
    const shareData = {
      title: `SkillSphere Technical Assessment: ${item.title}`,
      text: `Hello ${item.candidate_name || 'Candidate'}, you have been invited to complete a 20-question technical assessment for ${item.job_title || 'the position'}. Please access your exam here:`,
      url: url,
    };

    if (navigator.share && navigator.canShare && navigator.canShare(shareData)) {
      try {
        await navigator.share(shareData);
        showToast('Assessment link shared successfully!', 'success');
      } catch (err) {
        if (err.name !== 'AbortError') {
          await handleCopyLink(item.test_token);
        }
      }
    } else {
      await handleCopyLink(item.test_token);
    }
  };

  // Candidate Selection Helpers for Assignment
  const handleCandidateToggle = (candId) => {
    setSelectedCandidateIds((prev) =>
      prev.includes(candId) ? prev.filter((id) => id !== candId) : [...prev, candId]
    );
  };

  const handleSelectAllCandidates = (candList) => {
    const allIds = candList.map((c) => c.candidate_id);
    const areAllSelected = allIds.every((id) => selectedCandidateIds.includes(id));
    if (areAllSelected) {
      setSelectedCandidateIds((prev) => prev.filter((id) => !allIds.includes(id)));
    } else {
      setSelectedCandidateIds((prev) => Array.from(new Set([...prev, ...allIds])));
    }
  };

  // Submit Candidate Assignment
  const handleAssignSubmit = async (e) => {
    e?.preventDefault();
    if (selectedCandidateIds.length === 0) {
      showToast('Please select at least one candidate.', 'error');
      return;
    }
    if (!assignTitle.trim()) {
      showToast('Please enter an assessment title.', 'error');
      return;
    }

    setAssigning(true);
    try {
      const payload = {
        candidate_ids: selectedCandidateIds,
        job_id: assignJobId ? Number(assignJobId) : null,
        template_id: assignSource === 'template' && assignTemplateId ? Number(assignTemplateId) : null,
        title: assignTitle.trim(),
        description: assignDescription.trim() || null,
        tech_stack: assignTech.trim() || 'General Technical',
        duration_minutes: Number(assignDuration) || 25,
        passing_percentage: Number(assignPassPercent) || 60,
        expires_days: Number(assignExpiresDays) || 7,
        send_email: Boolean(assignSendEmail),
      };

      const res = await assessmentAPI.assignAssessment(payload);
      showToast(res.data.message || `Assigned to ${selectedCandidateIds.length} candidate(s)!`, 'success');
      setRecentAssignments(res.data.assignments || []);
      setSelectedCandidateIds([]);

      // Refresh tracking & candidates
      const [trackRes, candRes] = await Promise.all([
        assessmentAPI.getAssignedTracking(),
        assessmentAPI.getAssignableCandidates(),
      ]);
      setAssignedTracking(trackRes.data || []);
      setAssignableCandidates(candRes.data || []);
    } catch (err) {
      console.error('Assignment error:', err);
      showToast(err.response?.data?.detail || 'Failed to assign assessment to candidates.', 'error');
    } finally {
      setAssigning(false);
    }
  };

  // Generate Questions via AI (Gemini or Auto-Bank)
  const handleGenerateAIQuestions = async () => {
    if (!aiRole.trim()) {
      showToast('Please enter the target role (e.g. React Developer).', 'error');
      return;
    }
    setAiGenerating(true);
    try {
      const res = await assessmentAPI.generateQuestionsAI({
        role: aiRole.trim(),
        tech_stack: aiTech,
        count: Number(aiCount) || 5,
        difficulty: aiDiff,
      });

      const questionsList = res.data?.questions || [];
      setAiGeneratedQuestions(questionsList);
      const source = res.data?.source === 'gemini' ? 'Google Gemini 1.5 Flash' : 'Question Bank Engine';
      showToast(`Generated ${questionsList.length} MCQs via ${source}!`, 'success');
    } catch (err) {
      console.error('AI question generation error:', err);
      showToast(err.response?.data?.detail || 'Failed to generate questions with AI.', 'error');
    } finally {
      setAiGenerating(false);
    }
  };

  // Add AI questions into Question Bank
  const handleAddAIQuestionsToBank = async () => {
    if (aiGeneratedQuestions.length === 0) return;
    setSavingQuestion(true);
    try {
      let count = 0;
      for (const q of aiGeneratedQuestions) {
        await assessmentAPI.createQuestion({
          technology: q.technology || aiTech,
          difficulty: q.difficulty || aiDiff,
          question_text: q.question_text,
          options: q.options,
          correct_answer: q.correct_answer,
          explanation: q.explanation || 'Created with SkillSphere AI Studio',
          job_id: assessmentJobId ? Number(assessmentJobId) : null,
        });
        count++;
      }
      showToast(`Added ${count} questions to your Question Bank!`, 'success');
      setIsAIQuestionModalOpen(false);
      setAiGeneratedQuestions([]);
      await refreshQuestions();
    } catch (err) {
      console.error('Error saving AI questions:', err);
      showToast('Could not save some AI questions.', 'error');
    } finally {
      setSavingQuestion(false);
    }
  };

  if (loading) {
    return (
      <div className="py-24 text-center space-y-4">
        <div className="w-10 h-10 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin mx-auto" />
        <p className="text-slate-400 text-sm">Loading recruiter question bank & assessment controls...</p>
      </div>
    );
  }

  const publishedTemplates = templates.filter((t) => t.status === 'published');
  const draftTemplates = templates.filter((t) => t.status === 'draft');

  return (
    <div className="space-y-8">
      {/* ================= TOP RECRUITER ASSESSMENT TELEMETRY ================= */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div className="glass-card p-4 rounded-2xl border-white/10 text-center">
            <span className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold block mb-1">
              My Question Bank
            </span>
            <span className="text-2xl font-black text-cyan-400">{stats.total_questions}</span>
            <span className="text-[10px] text-slate-500 block mt-0.5">MCQs authored</span>
          </div>

          <div className="glass-card p-4 rounded-2xl border-emerald-500/30 bg-emerald-500/5 text-center">
            <span className="text-[11px] uppercase tracking-wider text-emerald-400 font-semibold block mb-1">
              Published Tests
            </span>
            <span className="text-2xl font-black text-emerald-400">{stats.published_assessments}</span>
            <span className="text-[10px] text-emerald-500/80 block mt-0.5">Active for jobs</span>
          </div>

          <div className="glass-card p-4 rounded-2xl border-amber-500/30 bg-amber-500/5 text-center">
            <span className="text-[11px] uppercase tracking-wider text-amber-400 font-semibold block mb-1">
              Draft Tests
            </span>
            <span className="text-2xl font-black text-amber-400">{stats.draft_assessments}</span>
            <span className="text-[10px] text-amber-500/80 block mt-0.5">In progress</span>
          </div>

          <div className="glass-card p-4 rounded-2xl border-white/10 text-center">
            <span className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold block mb-1">
              Candidates Tested
            </span>
            <span className="text-2xl font-black text-white">{stats.total_candidates_tested}</span>
            <span className="text-[10px] text-slate-500 block mt-0.5">{stats.tests_completed} Completed</span>
          </div>

          <div className="glass-card p-4 rounded-2xl border-purple-500/30 bg-purple-500/5 text-center">
            <span className="text-[11px] uppercase tracking-wider text-purple-400 font-semibold block mb-1">
              Candidates Passed
            </span>
            <span className="text-2xl font-black text-purple-400">{stats.tests_passed}</span>
            <span className="text-[10px] text-purple-500/80 block mt-0.5">Interview stage</span>
          </div>

          <div className="glass-card p-4 rounded-2xl border-cyan-500/30 bg-cyan-500/5 text-center">
            <span className="text-[11px] uppercase tracking-wider text-cyan-400 font-semibold block mb-1">
              Average Score
            </span>
            <span className="text-2xl font-black text-cyan-300">{stats.average_score}%</span>
            <span className="text-[10px] text-cyan-500/80 block mt-0.5">Evaluation accuracy</span>
          </div>
        </div>
      )}

      {/* ================= SUB-NAVIGATION TABS (6 SECTIONS) ================= */}
      <div className="flex border-b border-white/10 space-x-2 overflow-x-auto pb-1">
        <button
          onClick={() => setActiveTab('questions')}
          className={`pb-3 px-4 text-xs font-bold border-b-2 transition-all flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'questions'
              ? 'border-cyan-400 text-cyan-300'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <HelpCircle className="w-4 h-4" />
          <span>1. Manage Questions ({questions.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('create')}
          className={`pb-3 px-4 text-xs font-bold border-b-2 transition-all flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'create'
              ? 'border-cyan-400 text-cyan-300'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <Plus className="w-4 h-4" />
          <span>2. Create 20-Q Assessment</span>
          {selectedQuestionIds.length > 0 && (
            <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-cyan-500 text-black font-extrabold">
              {selectedQuestionIds.length}/20
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab('assign')}
          className={`pb-3 px-4 text-xs font-bold border-b-2 transition-all flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'assign'
              ? 'border-cyan-400 text-cyan-300'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>3. Assign to Candidates & Share Link</span>
          {assignableCandidates.length > 0 && (
            <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-cyan-500/20 text-cyan-300 font-extrabold border border-cyan-500/30">
              {assignableCandidates.length}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab('tracking')}
          className={`pb-3 px-4 text-xs font-bold border-b-2 transition-all flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'tracking'
              ? 'border-indigo-400 text-indigo-300'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <Clock className="w-4 h-4" />
          <span>4. Assigned Tracking ({assignedTracking.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('published')}
          className={`pb-3 px-4 text-xs font-bold border-b-2 transition-all flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'published'
              ? 'border-emerald-400 text-emerald-300'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <CheckCircle2 className="w-4 h-4" />
          <span>5. Published Tests ({publishedTemplates.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('drafts')}
          className={`pb-3 px-4 text-xs font-bold border-b-2 transition-all flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'drafts'
              ? 'border-amber-400 text-amber-300'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>6. Drafts ({draftTemplates.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('results')}
          className={`pb-3 px-4 text-xs font-bold border-b-2 transition-all flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'results'
              ? 'border-purple-400 text-purple-300'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <Award className="w-4 h-4" />
          <span>7. Answer Sheets ({candidateResults.length})</span>
        </button>
      </div>

      {/* ================= TAB 1: MANAGE QUESTIONS ================= */}
      {activeTab === 'questions' && (
        <div className="space-y-6">
          {/* Header & Action Controls */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h3 className="text-xl font-bold font-heading text-white flex items-center gap-2">
                <BrainCircuit className="w-5 h-5 text-cyan-400" />
                Manage Assessment Questions
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Author custom questions, specify exact MCQ options and answers, and manage your technical inventory.
              </p>
            </div>

            <div className="flex items-center gap-2 flex-wrap">
              <button
                onClick={() => setIsAIQuestionModalOpen(true)}
                className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-purple-500/20 to-cyan-500/20 hover:from-purple-500/30 hover:to-cyan-500/30 border border-purple-500/30 text-purple-200 flex items-center gap-1.5 transition-all shadow-md"
              >
                <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                <span>Generate with AI</span>
              </button>

              <button
                onClick={() => setIsImportLibraryOpen(true)}
                className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 flex items-center gap-1.5 transition-colors"
              >
                <Download className="w-3.5 h-3.5 text-cyan-400" />
                <span>Import from Library</span>
              </button>

              <button
                onClick={handleOpenCreateQuestion}
                className="px-4 py-2 rounded-xl text-xs font-bold bg-cyan-500 hover:bg-cyan-400 text-black flex items-center gap-1.5 shadow-lg shadow-cyan-500/20 transition-all"
              >
                <Plus className="w-4 h-4" />
                <span>Create New Question</span>
              </button>
            </div>
          </div>

          {/* Search & Filters */}
          <div className="p-4 rounded-2xl glass-card border border-white/10 flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-1.5">
                <span className="text-slate-400">Tech:</span>
                <select
                  value={techFilter}
                  onChange={(e) => setTechFilter(e.target.value)}
                  className="bg-dark-850 border border-white/10 text-white rounded-lg px-2.5 py-1.5 text-xs"
                >
                  {TECHNOLOGIES.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-1.5">
                <span className="text-slate-400">Difficulty:</span>
                <select
                  value={diffFilter}
                  onChange={(e) => setDiffFilter(e.target.value)}
                  className="bg-dark-850 border border-white/10 text-white rounded-lg px-2.5 py-1.5 text-xs"
                >
                  {DIFFICULTIES.map((d) => (
                    <option key={d} value={d}>{d.toUpperCase()}</option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-1.5">
                <span className="text-slate-400">Job:</span>
                <select
                  value={jobFilter}
                  onChange={(e) => setJobFilter(e.target.value)}
                  className="bg-dark-850 border border-white/10 text-white rounded-lg px-2.5 py-1.5 text-xs max-w-[180px]"
                >
                  <option value="">All Jobs / General</option>
                  {jobs.map((j) => (
                    <option key={j.job_id} value={j.job_id}>{j.title}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search question text..."
                value={questionSearch}
                onChange={(e) => setQuestionSearch(e.target.value)}
                className="pl-8 pr-3 py-1.5 rounded-lg glass-input text-xs w-56 text-white"
              />
            </div>
          </div>

          {/* Questions List */}
          {questions.length === 0 ? (
            <div className="p-12 text-center rounded-2xl glass-card border border-white/10">
              <HelpCircle className="w-12 h-12 text-slate-500 mx-auto mb-3" />
              <h3 className="text-base font-bold text-white mb-1">No questions found in this view</h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto mb-4">
                Create custom questions or click "Import from Library" to pull curated technical questions into your bank.
              </p>
              <button
                onClick={() => setIsImportLibraryOpen(true)}
                className="px-4 py-2 rounded-xl text-xs font-bold bg-cyan-500 text-black hover:bg-cyan-400"
              >
                Import Python / React / MERN Library
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {questions.map((q, idx) => (
                <div
                  key={q.question_id}
                  className="p-5 rounded-2xl glass-card border border-white/10 hover:border-cyan-500/30 transition-all flex flex-col md:flex-row md:items-start justify-between gap-4"
                >
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-mono text-xs font-bold text-slate-500">#{idx + 1}</span>
                      <span className="px-2 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                        {q.technology}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                        q.difficulty === 'beginner' ? 'bg-emerald-500/15 text-emerald-300' :
                        q.difficulty === 'intermediate' ? 'bg-purple-500/15 text-purple-300' :
                        'bg-amber-500/15 text-amber-300'
                      }`}>
                        {q.difficulty}
                      </span>
                      {q.job_title && (
                        <span className="text-[11px] text-slate-400 flex items-center gap-1">
                          <Briefcase className="w-3 h-3 text-slate-500" /> {q.job_title}
                        </span>
                      )}
                    </div>

                    <h4 className="text-sm md:text-base font-bold text-white leading-relaxed">
                      {q.question_text}
                    </h4>

                    {/* 4 Options Grid */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2 text-xs">
                      {(q.options || []).map((opt, oIdx) => {
                        const isCorrect = opt === q.correct_answer;
                        const letter = String.fromCharCode(65 + oIdx);
                        return (
                          <div
                            key={oIdx}
                            className={`p-2.5 rounded-xl border flex items-center gap-2 ${
                              isCorrect
                                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300 font-semibold'
                                : 'bg-black/20 border-white/5 text-slate-300'
                            }`}
                          >
                            <span className={`w-5 h-5 rounded flex items-center justify-center font-mono text-[10px] shrink-0 ${
                              isCorrect ? 'bg-emerald-500 text-black font-black' : 'bg-white/10 text-slate-400'
                            }`}>
                              {letter}
                            </span>
                            <span className="truncate">{opt}</span>
                            {isCorrect && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 ml-auto shrink-0" />}
                          </div>
                        );
                      })}
                    </div>

                    {q.explanation && (
                      <p className="text-[11px] text-slate-400 font-mono bg-black/30 p-2 rounded-lg border border-white/5 mt-2">
                        <strong className="text-slate-300">Explanation:</strong> {q.explanation}
                      </p>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 self-end md:self-start shrink-0 pt-2 md:pt-0">
                    <button
                      onClick={() => handleOpenEditQuestion(q)}
                      className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 hover:text-white transition-colors"
                      title="Edit Question"
                    >
                      <Edit3 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteQuestion(q.question_id)}
                      className="p-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 transition-colors"
                      title="Delete Question"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ================= TAB 2: CREATE 20-QUESTION ASSESSMENT ================= */}
      {activeTab === 'create' && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h3 className="text-xl font-bold font-heading text-white flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-cyan-400" />
                {editingTemplateId ? 'Edit Assessment Template' : 'Create Recruiter-Controlled Assessment'}
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Hand-pick exactly 20 technical questions from your question bank for this job opening.
              </p>
            </div>

            {/* Counter Badge */}
            <div className={`px-4 py-2 rounded-2xl border flex items-center gap-3 ${
              selectedQuestionIds.length === 20
                ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-300'
                : 'bg-amber-500/10 border-amber-500/40 text-amber-300'
            }`}>
              <div className="text-right">
                <span className="text-[10px] uppercase font-bold tracking-wider block">Question Quota</span>
                <span className="text-base font-black">
                  {selectedQuestionIds.length} / 20 Selected
                </span>
              </div>
              {selectedQuestionIds.length === 20 ? (
                <CheckCircle2 className="w-6 h-6 text-emerald-400" />
              ) : (
                <span className="text-xs font-semibold">({20 - selectedQuestionIds.length} remaining)</span>
              )}
            </div>
          </div>

          {/* Assessment Metadata Settings */}
          <div className="glass-card p-6 rounded-2xl border border-white/10 space-y-4">
            <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-400">
              Assessment Configuration
            </h4>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Target Job Opening</label>
                <select
                  value={assessmentJobId}
                  onChange={(e) => {
                    const jid = e.target.value;
                    setAssessmentJobId(jid);
                    const selJob = jobs.find((j) => j.job_id === Number(jid));
                    if (selJob) {
                      setAssessmentTitle(`${selJob.title} Technical Evaluation`);
                      setAssessmentTech(selJob.skills?.[0] || 'Full Stack');
                    }
                  }}
                  className="w-full bg-dark-850 border border-white/10 text-white rounded-xl px-3 py-2 text-xs"
                >
                  {jobs.map((j) => (
                    <option key={j.job_id} value={j.job_id}>{j.title} ({j.company_name})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Assessment Title</label>
                <input
                  type="text"
                  value={assessmentTitle}
                  onChange={(e) => setAssessmentTitle(e.target.value)}
                  placeholder="e.g. Senior Backend Python Evaluation"
                  className="w-full glass-input px-3 py-2 rounded-xl text-xs text-white"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Duration (Minutes)</label>
                <input
                  type="number"
                  min="10"
                  max="120"
                  value={assessmentDuration}
                  onChange={(e) => setAssessmentDuration(e.target.value)}
                  className="w-full glass-input px-3 py-2 rounded-xl text-xs text-white"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Passing Mark (%)</label>
                <input
                  type="number"
                  min="40"
                  max="100"
                  value={assessmentPassPercent}
                  onChange={(e) => setAssessmentPassPercent(e.target.value)}
                  className="w-full glass-input px-3 py-2 rounded-xl text-xs text-white"
                />
              </div>
            </div>

            {/* Quick Action Buttons */}
            <div className="flex items-center justify-between pt-4 border-t border-white/10 flex-wrap gap-3">
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setSelectedQuestionIds([])}
                  className="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-xs text-slate-400"
                >
                  Clear Selection
                </button>
                <button
                  type="button"
                  onClick={() => {
                    const first20 = questions.slice(0, 20).map((q) => q.question_id);
                    setSelectedQuestionIds(first20);
                  }}
                  className="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-xs text-cyan-300"
                >
                  Auto-Select First 20
                </button>
              </div>

              <div className="flex items-center gap-3">
                <button
                  disabled={savingAssessment}
                  onClick={() => handleSaveAssessment('draft')}
                  className="px-5 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-slate-200 text-xs font-bold transition-all disabled:opacity-50"
                >
                  Save as Draft
                </button>

                <button
                  disabled={savingAssessment || selectedQuestionIds.length !== 20}
                  onClick={() => handleSaveAssessment('published')}
                  className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-black text-xs font-black shadow-lg shadow-emerald-500/20 hover:brightness-110 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Publish 20-Question Assessment</span>
                </button>
              </div>
            </div>
          </div>

          {/* Interactive Question Selector (Pick 20 Questions) */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-bold text-white flex items-center gap-2">
                <Layers className="w-4 h-4 text-cyan-400" />
                Select Questions from Bank ({selectedQuestionIds.length}/20 selected)
              </h4>
              <span className="text-xs text-slate-400">Click a card to toggle selection</span>
            </div>

            <div className="space-y-2">
              {questions.map((q) => {
                const isSelected = selectedQuestionIds.includes(q.question_id);

                return (
                  <div
                    key={q.question_id}
                    onClick={() => handleToggleSelectQuestion(q.question_id)}
                    className={`p-4 rounded-xl border transition-all cursor-pointer flex items-start gap-4 ${
                      isSelected
                        ? 'bg-cyan-500/10 border-cyan-400 ring-1 ring-cyan-500/40 text-white shadow-md shadow-cyan-500/10'
                        : 'bg-dark-850/60 border-white/10 text-slate-300 hover:border-white/30'
                    }`}
                  >
                    <div className={`w-5 h-5 rounded-md flex items-center justify-center shrink-0 mt-0.5 border ${
                      isSelected ? 'bg-cyan-500 border-cyan-400 text-black' : 'border-white/20'
                    }`}>
                      {isSelected && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                    </div>

                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-white/10 text-slate-300">
                          {q.technology}
                        </span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                          q.difficulty === 'beginner' ? 'text-emerald-400 bg-emerald-500/10' :
                          q.difficulty === 'intermediate' ? 'text-purple-400 bg-purple-500/10' :
                          'text-amber-400 bg-amber-500/10'
                        }`}>
                          {q.difficulty}
                        </span>
                        <span className="text-xs text-emerald-400 font-semibold">
                          Correct: {q.correct_answer}
                        </span>
                      </div>
                      <p className="text-xs font-semibold text-white leading-relaxed">
                        {q.question_text}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* ================= TAB: ASSIGN ASSESSMENT TO CANDIDATES ================= */}
      {activeTab === 'assign' && (
        <div className="space-y-8">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h3 className="text-xl font-bold font-heading text-white flex items-center gap-2">
                <Users className="w-5 h-5 text-cyan-400" />
                Assign Assessment to Candidates
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Directly invite candidates to technical assessments. Generates unique secure links with instant Copy and Share tools.
              </p>
            </div>

            <button
              onClick={() => setActiveTab('tracking')}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-white/5 hover:bg-white/10 text-cyan-300 border border-cyan-500/30 flex items-center gap-1.5 self-start sm:self-auto"
            >
              <Clock className="w-3.5 h-3.5" />
              <span>View Tracking Dashboard ({assignedTracking.length})</span>
            </button>
          </div>

          {/* Success Banner: Newly Generated Test Links */}
          {recentAssignments.length > 0 && (
            <div className="p-6 rounded-3xl glass-card border border-emerald-500/40 bg-emerald-500/10 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <h4 className="text-sm font-bold text-white">
                    Successfully Generated {recentAssignments.length} Candidate Test Link(s)!
                  </h4>
                </div>
                <button
                  onClick={() => setRecentAssignments([])}
                  className="text-xs text-slate-400 hover:text-white"
                >
                  Dismiss
                </button>
              </div>

              <div className="space-y-2">
                {recentAssignments.map((a) => (
                  <div
                    key={a.test_token}
                    className="p-3.5 rounded-2xl bg-black/40 border border-white/10 flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs"
                  >
                    <div>
                      <span className="font-bold text-white">{a.candidate_name}</span>
                      <span className="text-slate-400 ml-2">({a.candidate_email})</span>
                      <span className="text-[11px] text-cyan-300 block mt-0.5">{a.title}</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <div className="px-2.5 py-1.5 rounded-lg bg-black/60 border border-white/10 font-mono text-[11px] text-slate-300 select-all max-w-xs truncate">
                        {a.test_link}
                      </div>

                      <button
                        onClick={() => handleCopyLink(a.test_token)}
                        className={`px-3 py-1.5 rounded-xl font-bold text-xs flex items-center gap-1.5 transition-all ${
                          copiedToken === a.test_token
                            ? 'bg-emerald-500 text-black'
                            : 'bg-white/10 hover:bg-white/20 text-white'
                        }`}
                      >
                        {copiedToken === a.test_token ? (
                          <>
                            <Check className="w-3.5 h-3.5 text-black" />
                            <span>Copied!</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3.5 h-3.5" />
                            <span>Copy Link</span>
                          </>
                        )}
                      </button>

                      <button
                        onClick={() => handleShareLink(a)}
                        className="px-3 py-1.5 rounded-xl font-bold text-xs bg-cyan-500 hover:bg-cyan-400 text-black flex items-center gap-1.5 transition-all shadow-md shadow-cyan-500/20"
                      >
                        <Share2 className="w-3.5 h-3.5" />
                        <span>Share</span>
                      </button>

                      <a
                        href={a.test_link}
                        target="_blank"
                        rel="noreferrer"
                        className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300"
                        title="Simulate / Open Test"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Assignment Configuration Form */}
          <form onSubmit={handleAssignSubmit} className="space-y-6">
            <div className="p-6 rounded-3xl glass-card border border-white/10 space-y-4">
              <span className="text-xs font-bold uppercase text-cyan-400 tracking-wider block">
                Step 1: Configure Assessment Parameters
              </span>

              {/* Source Switch */}
              <div className="flex items-center gap-3 pb-3 border-b border-white/10">
                <button
                  type="button"
                  onClick={() => setAssignSource('template')}
                  className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                    assignSource === 'template'
                      ? 'bg-cyan-500 text-black shadow-lg shadow-cyan-500/20'
                      : 'bg-white/5 hover:bg-white/10 text-slate-300'
                  }`}
                >
                  Use Published 20-Q Template
                </button>
                <button
                  type="button"
                  onClick={() => setAssignSource('custom')}
                  className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                    assignSource === 'custom'
                      ? 'bg-cyan-500 text-black shadow-lg shadow-cyan-500/20'
                      : 'bg-white/5 hover:bg-white/10 text-slate-300'
                  }`}
                >
                  Custom Assessment / Tech Stack
                </button>
              </div>

              {assignSource === 'template' ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  <div>
                    <label className="block text-slate-300 font-semibold mb-1">Select Published Assessment</label>
                    <select
                      value={assignTemplateId}
                      onChange={(e) => {
                        const tid = e.target.value;
                        setAssignTemplateId(tid);
                        const selTmpl = publishedTemplates.find((t) => t.template_id === Number(tid));
                        if (selTmpl) {
                          setAssignTitle(selTmpl.title);
                          setAssignJobId(selTmpl.job_id);
                          setAssignTech(selTmpl.tech_stack);
                          setAssignDuration(selTmpl.duration_minutes || 25);
                          setAssignPassPercent(selTmpl.passing_percentage || 60);
                        }
                      }}
                      className="w-full bg-dark-850 border border-white/10 text-white rounded-xl px-3 py-2 text-xs"
                    >
                      {publishedTemplates.length === 0 ? (
                        <option value="">No published templates available (Switch to Custom)</option>
                      ) : (
                        publishedTemplates.map((t) => (
                          <option key={t.template_id} value={t.template_id}>
                            {t.title} ({t.job_title} - 20 Qs)
                          </option>
                        ))
                      )}
                    </select>
                  </div>

                  <div>
                    <label className="block text-slate-300 font-semibold mb-1">Associated Job Opening</label>
                    <select
                      value={assignJobId}
                      onChange={(e) => setAssignJobId(e.target.value)}
                      className="w-full bg-dark-850 border border-white/10 text-white rounded-xl px-3 py-2 text-xs"
                    >
                      <option value="">General Assessment (No Job)</option>
                      {jobs.map((j) => (
                        <option key={j.job_id} value={j.job_id}>
                          {j.title} ({j.company_name})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                  <div>
                    <label className="block text-slate-300 font-semibold mb-1">Assessment Title *</label>
                    <input
                      type="text"
                      required
                      value={assignTitle}
                      onChange={(e) => setAssignTitle(e.target.value)}
                      placeholder="e.g. Senior Full Stack Engineer Technical Test"
                      className="w-full glass-input px-3 py-2 rounded-xl text-xs text-white"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-300 font-semibold mb-1">Associated Job</label>
                    <select
                      value={assignJobId}
                      onChange={(e) => setAssignJobId(e.target.value)}
                      className="w-full bg-dark-850 border border-white/10 text-white rounded-xl px-3 py-2 text-xs"
                    >
                      <option value="">General Assessment</option>
                      {jobs.map((j) => (
                        <option key={j.job_id} value={j.job_id}>
                          {j.title}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-slate-300 font-semibold mb-1">Primary Technology</label>
                    <select
                      value={assignTech}
                      onChange={(e) => setAssignTech(e.target.value)}
                      className="w-full bg-dark-850 border border-white/10 text-white rounded-xl px-3 py-2 text-xs"
                    >
                      {TECHNOLOGIES.filter((t) => t !== 'All').map((t) => (
                        <option key={t} value={t}>
                          {t}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              )}

              {/* Assessment Description */}
              <div>
                <label className="block text-slate-300 font-semibold mb-1 text-xs">
                  Description / Instructions for Candidate (Optional)
                </label>
                <textarea
                  rows="2"
                  value={assignDescription}
                  onChange={(e) => setAssignDescription(e.target.value)}
                  placeholder="Instructions, guidelines, or focus areas for the candidate..."
                  className="w-full glass-input px-3 py-2 rounded-xl text-xs text-white"
                />
              </div>

              {/* Specs & Validity */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs pt-2">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Time Limit (Minutes)</label>
                  <input
                    type="number"
                    min="10"
                    max="180"
                    value={assignDuration}
                    onChange={(e) => setAssignDuration(e.target.value)}
                    className="w-full glass-input px-3 py-2 rounded-xl text-xs text-white"
                  />
                </div>

                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Passing Mark (%)</label>
                  <input
                    type="number"
                    min="20"
                    max="100"
                    value={assignPassPercent}
                    onChange={(e) => setAssignPassPercent(e.target.value)}
                    className="w-full glass-input px-3 py-2 rounded-xl text-xs text-white"
                  />
                </div>

                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Link Validity / Deadline</label>
                  <select
                    value={assignExpiresDays}
                    onChange={(e) => setAssignExpiresDays(e.target.value)}
                    className="w-full bg-dark-850 border border-white/10 text-white rounded-xl px-3 py-2 text-xs"
                  >
                    <option value="3">3 Days Validity</option>
                    <option value="7">7 Days Validity (Default)</option>
                    <option value="14">14 Days Validity</option>
                    <option value="30">30 Days Validity</option>
                  </select>
                </div>
              </div>

              {/* Email dispatch toggle */}
              <div className="pt-2">
                <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-300 select-none">
                  <input
                    type="checkbox"
                    checked={assignSendEmail}
                    onChange={(e) => setAssignSendEmail(e.target.checked)}
                    className="w-4 h-4 rounded text-cyan-500 bg-dark-850 border-white/20"
                  />
                  <Mail className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Send invitation email notification with test link to candidate</span>
                </label>
              </div>
            </div>

            {/* Candidate Selection Matrix */}
            <div className="p-6 rounded-3xl glass-card border border-white/10 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <span className="text-xs font-bold uppercase text-cyan-400 tracking-wider block">
                    Step 2: Select Job Seekers to Assign
                  </span>
                  <span className="text-xs text-slate-400">
                    {selectedCandidateIds.length} candidate(s) selected
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      const filtered = assignableCandidates.filter((c) => {
                        const matchesSearch =
                          !candidateSearch ||
                          c.name.toLowerCase().includes(candidateSearch.toLowerCase()) ||
                          c.email.toLowerCase().includes(candidateSearch.toLowerCase()) ||
                          c.skills.some((s) => s.toLowerCase().includes(candidateSearch.toLowerCase()));
                        return matchesSearch;
                      });
                      handleSelectAllCandidates(filtered);
                    }}
                    className="px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-xs text-slate-300 border border-white/10"
                  >
                    Toggle All Filtered
                  </button>
                  {selectedCandidateIds.length > 0 && (
                    <button
                      type="button"
                      onClick={() => setSelectedCandidateIds([])}
                      className="px-3 py-1.5 rounded-xl bg-rose-500/10 text-rose-300 hover:bg-rose-500/20 text-xs"
                    >
                      Clear Selection
                    </button>
                  )}
                </div>
              </div>

              {/* Filter controls */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div className="relative">
                  <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={candidateSearch}
                    onChange={(e) => setCandidateSearch(e.target.value)}
                    placeholder="Search candidates by name, email, or skill..."
                    className="w-full glass-input pl-9 pr-3 py-2 rounded-xl text-xs text-white"
                  />
                </div>

                <select
                  value={candidateJobFilter}
                  onChange={(e) => setCandidateJobFilter(e.target.value)}
                  className="bg-dark-850 border border-white/10 text-white rounded-xl px-3 py-2 text-xs"
                >
                  <option value="">All Applied Jobs</option>
                  {jobs.map((j) => (
                    <option key={j.job_id} value={j.job_id}>
                      Applicants for: {j.title}
                    </option>
                  ))}
                </select>
              </div>

              {/* Candidate Cards List */}
              {assignableCandidates.length === 0 ? (
                <div className="p-8 text-center text-xs text-slate-400">
                  No registered candidates found.
                </div>
              ) : (
                <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
                  {assignableCandidates
                    .filter((c) => {
                      const matchesSearch =
                        !candidateSearch ||
                        c.name.toLowerCase().includes(candidateSearch.toLowerCase()) ||
                        c.email.toLowerCase().includes(candidateSearch.toLowerCase()) ||
                        c.skills.some((s) => s.toLowerCase().includes(candidateSearch.toLowerCase()));
                      const matchesJob =
                        !candidateJobFilter ||
                        c.applications.some((app) => app.job_id === Number(candidateJobFilter));
                      return matchesSearch && matchesJob;
                    })
                    .map((c) => {
                      const isSelected = selectedCandidateIds.includes(c.candidate_id);
                      return (
                        <div
                          key={c.candidate_id}
                          onClick={() => handleCandidateToggle(c.candidate_id)}
                          className={`p-3.5 rounded-2xl border transition-all cursor-pointer flex items-center justify-between gap-4 text-xs ${
                            isSelected
                              ? 'bg-cyan-500/10 border-cyan-500/40 ring-1 ring-cyan-500/30'
                              : 'bg-white/[0.02] border-white/5 hover:border-white/15'
                          }`}
                        >
                          <div className="flex items-center gap-3">
                            <div className="shrink-0">
                              {isSelected ? (
                                <CheckSquare className="w-4 h-4 text-cyan-400" />
                              ) : (
                                <Square className="w-4 h-4 text-slate-500" />
                              )}
                            </div>

                            <div>
                              <div className="flex items-center gap-2">
                                <span className="font-bold text-white">{c.name}</span>
                                <span className="text-slate-400 text-[11px]">{c.email}</span>
                                {c.location && (
                                  <span className="text-slate-500 text-[10px]">• {c.location}</span>
                                )}
                              </div>

                              <div className="flex flex-wrap items-center gap-1 mt-1.5">
                                {(c.skills || []).slice(0, 5).map((s) => (
                                  <span
                                    key={s}
                                    className="px-2 py-0.5 rounded text-[10px] font-medium bg-white/10 text-slate-300"
                                  >
                                    {s}
                                  </span>
                                ))}
                                {c.skills && c.skills.length > 5 && (
                                  <span className="text-[10px] text-slate-500">
                                    +{c.skills.length - 5} more
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>

                          <div className="text-right shrink-0">
                            {c.experience && (
                              <span className="text-slate-300 block font-medium text-[11px]">
                                {c.experience}
                              </span>
                            )}
                            <span className="text-slate-500 text-[10px]">
                              {c.assigned_tests ? `${c.assigned_tests.length} tests assigned` : 'No prior tests'}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                </div>
              )}
            </div>

            {/* Submit Action */}
            <div className="flex items-center justify-end gap-3 pt-4">
              <button
                type="submit"
                disabled={assigning || selectedCandidateIds.length === 0}
                className={`px-6 py-3 rounded-2xl font-bold text-xs flex items-center gap-2 shadow-xl transition-all ${
                  assigning || selectedCandidateIds.length === 0
                    ? 'bg-white/10 text-slate-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-cyan-500 to-blue-600 text-black shadow-cyan-500/25 hover:brightness-110'
                }`}
              >
                {assigning ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Assigning & Generating Test Links...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Assign Assessment to {selectedCandidateIds.length} Candidate(s)</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* ================= TAB: ASSIGNED CANDIDATES TRACKING ================= */}
      {activeTab === 'tracking' && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h3 className="text-xl font-bold font-heading text-white flex items-center gap-2">
                <Clock className="w-5 h-5 text-indigo-400" />
                Assigned Candidates Tracking Dashboard
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Track candidate test assignments, active attempt status, expiration deadlines, and access links.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveTab('assign')}
                className="px-4 py-2 rounded-xl text-xs font-bold bg-cyan-500 hover:bg-cyan-400 text-black flex items-center gap-1.5 shadow-lg shadow-cyan-500/20"
              >
                <Plus className="w-4 h-4" />
                <span>Assign New Assessment</span>
              </button>

              <button
                onClick={async () => {
                  const res = await assessmentAPI.getAssignedTracking();
                  setAssignedTracking(res.data || []);
                  showToast('Tracking data refreshed!', 'info');
                }}
                className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 border border-white/10"
                title="Refresh Tracking"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Search & Filter Bar */}
          <div className="p-4 rounded-2xl glass-card border border-white/10 grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={trackingSearch}
                onChange={(e) => setTrackingSearch(e.target.value)}
                placeholder="Search candidate name, email, or test..."
                className="w-full glass-input pl-9 pr-3 py-2 rounded-xl text-xs text-white"
              />
            </div>

            <select
              value={trackingStatusFilter}
              onChange={(e) => setTrackingStatusFilter(e.target.value)}
              className="bg-dark-850 border border-white/10 text-white rounded-xl px-3 py-2 text-xs"
            >
              <option value="all">All Statuses</option>
              <option value="pending">Pending Attempt</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="terminated_proctoring">Terminated (Proctoring)</option>
              <option value="expired">Expired</option>
            </select>

            <select
              value={trackingJobFilter}
              onChange={(e) => setTrackingJobFilter(e.target.value)}
              className="bg-dark-850 border border-white/10 text-white rounded-xl px-3 py-2 text-xs"
            >
              <option value="">All Job Openings</option>
              {jobs.map((j) => (
                <option key={j.job_id} value={j.job_id}>
                  {j.title}
                </option>
              ))}
            </select>
          </div>

          {/* Tracking List Table / Cards */}
          {assignedTracking.length === 0 ? (
            <div className="p-12 text-center rounded-2xl glass-card border border-white/10">
              <Clock className="w-12 h-12 text-slate-500 mx-auto mb-3" />
              <h3 className="text-base font-bold text-white mb-1">No assigned assessments found</h3>
              <p className="text-xs text-slate-400 mb-4">
                Assign an assessment to job seekers to generate secure test links and monitor progress.
              </p>
              <button
                onClick={() => setActiveTab('assign')}
                className="px-5 py-2.5 rounded-xl text-xs font-bold bg-cyan-500 text-black hover:bg-cyan-400"
              >
                Assign Assessment Now
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {assignedTracking
                .filter((item) => {
                  const s = trackingSearch.toLowerCase();
                  const matchesSearch =
                    !s ||
                    item.candidate_name?.toLowerCase().includes(s) ||
                    item.candidate_email?.toLowerCase().includes(s) ||
                    item.title?.toLowerCase().includes(s);
                  const matchesStatus =
                    trackingStatusFilter === 'all' || item.status === trackingStatusFilter;
                  const matchesJob =
                    !trackingJobFilter || item.job_id === Number(trackingJobFilter);
                  return matchesSearch && matchesStatus && matchesJob;
                })
                .map((item) => {
                  const isCompleted = item.status === 'completed';
                  const isTerminated = item.status === 'terminated_proctoring';
                  const isExpired = item.status === 'expired';
                  const isInProgress = item.status === 'in_progress';
                  const isPassed = item.passed;

                  return (
                    <div
                      key={item.assessment_id}
                      className="p-5 rounded-2xl glass-card border border-white/10 hover:border-white/20 transition-all flex flex-col lg:flex-row lg:items-center justify-between gap-4"
                    >
                      {/* Left: Candidate & Assessment Details */}
                      <div className="space-y-1.5 flex-1">
                        <div className="flex items-center gap-2.5 flex-wrap">
                          <h4 className="text-base font-bold text-white">{item.candidate_name}</h4>
                          <span className="text-xs text-slate-400">({item.candidate_email})</span>

                          {/* Status Badge */}
                          <span
                            className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider flex items-center gap-1 ${
                              isExpired
                                ? 'bg-slate-700/60 text-slate-400 border border-slate-600'
                                : isTerminated
                                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                                : isCompleted
                                ? isPassed
                                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                                  : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                                : isInProgress
                                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 animate-pulse'
                                : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                            }`}
                          >
                            {isExpired ? (
                              <>
                                <AlertTriangle className="w-3 h-3" /> Expired
                              </>
                            ) : isTerminated ? (
                              <>
                                <ShieldAlert className="w-3 h-3" /> Terminated (Proctoring)
                              </>
                            ) : isCompleted ? (
                              isPassed ? 'Passed' : 'Under Review'
                            ) : isInProgress ? (
                              <>
                                <Clock className="w-3 h-3" /> In Progress
                              </>
                            ) : (
                              'Pending Attempt'
                            )}
                          </span>
                        </div>

                        <p className="text-xs text-slate-300 flex items-center gap-2">
                          <Briefcase className="w-3.5 h-3.5 text-cyan-400" />
                          <span>{item.job_title}</span>
                          <span>•</span>
                          <span className="font-semibold text-white">{item.title}</span>
                        </p>

                        {/* Dates row */}
                        <div className="flex flex-wrap items-center gap-4 text-[11px] text-slate-400 pt-1">
                          <span>
                            Assigned: {new Date(item.created_at).toLocaleDateString()}
                          </span>
                          {item.expires_at && (
                            <span className={isExpired ? 'text-rose-400 font-semibold' : ''}>
                              Deadline: {new Date(item.expires_at).toLocaleDateString()}
                            </span>
                          )}
                          {item.completed_at && (
                            <span>
                              Completed: {new Date(item.completed_at).toLocaleDateString()}
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Right: Score & Actions */}
                      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 justify-between lg:justify-end border-t lg:border-t-0 pt-3 lg:pt-0 border-white/10 shrink-0">
                        {isCompleted && (
                          <div className="text-right">
                            <span className="text-[10px] uppercase text-slate-400 font-bold block">
                              Score
                            </span>
                            <span
                              className={`text-lg font-black ${
                                isPassed ? 'text-emerald-400' : 'text-amber-400'
                              }`}
                            >
                              {item.score}/{item.total_questions || 20} ({item.percentage}%)
                            </span>
                          </div>
                        )}

                        <div className="flex items-center gap-2 flex-wrap">
                          {/* Copy Link */}
                          <button
                            onClick={() => handleCopyLink(item.test_token)}
                            className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all ${
                              copiedToken === item.test_token
                                ? 'bg-emerald-500 text-black'
                                : 'bg-white/5 hover:bg-white/10 text-slate-300 border border-white/10'
                            }`}
                            title="Copy Candidate Assessment Link"
                          >
                            {copiedToken === item.test_token ? (
                              <>
                                <Check className="w-3 h-3 text-black" />
                                <span>Copied!</span>
                              </>
                            ) : (
                              <>
                                <Copy className="w-3 h-3" />
                                <span>Copy Link</span>
                              </>
                            )}
                          </button>

                          {/* Share Button */}
                          <button
                            onClick={() => handleShareLink(item)}
                            className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-white/5 hover:bg-white/10 text-slate-300 border border-white/10 flex items-center gap-1.5 transition-all"
                            title="Share Link via Native Browser Share"
                          >
                            <Share2 className="w-3 h-3 text-cyan-400" />
                            <span>Share</span>
                          </button>

                          {/* View Results Breakdown */}
                          {(isCompleted || isTerminated) && (
                            <button
                              onClick={() => handleInspectResults(item.assessment_id)}
                              className="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-white/10 hover:bg-white/20 text-white flex items-center gap-1.5"
                            >
                              <Eye className="w-3.5 h-3.5" />
                              <span>View Results</span>
                            </button>
                          )}

                          {/* Simulate / Open */}
                          <a
                            href={item.test_link}
                            target="_blank"
                            rel="noreferrer"
                            className="p-1.5 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300"
                            title="Simulate candidate view"
                          >
                            <ExternalLink className="w-3.5 h-3.5" />
                          </a>
                        </div>
                      </div>
                    </div>
                  );
                })}
            </div>
          )}
        </div>
      )}

      {/* ================= TAB 5: MY PUBLISHED ASSESSMENTS ================= */}
      {activeTab === 'published' && (
        <div className="space-y-6">
          <div>
            <h3 className="text-xl font-bold font-heading text-white flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              My Published Technical Assessments
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Active technical assessments automatically dispatched to candidates who achieve &ge; 70% screening match.
            </p>
          </div>

          {publishedTemplates.length === 0 ? (
            <div className="p-12 text-center rounded-2xl glass-card border border-white/10">
              <CheckCircle2 className="w-12 h-12 text-slate-500 mx-auto mb-3" />
              <h3 className="text-base font-bold text-white mb-1">No published assessments yet</h3>
              <p className="text-xs text-slate-400 mb-4">
                Create and publish a 20-question assessment so shortlisted candidates can be evaluated.
              </p>
              <button
                onClick={() => setActiveTab('create')}
                className="px-5 py-2.5 rounded-xl text-xs font-bold bg-cyan-500 text-black hover:bg-cyan-400"
              >
                Create First Assessment
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {publishedTemplates.map((t) => (
                <div
                  key={t.template_id}
                  className="p-6 rounded-3xl glass-card border border-emerald-500/30 bg-emerald-500/5 flex flex-col justify-between"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-3">
                      <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 uppercase tracking-wider">
                        Published & Active
                      </span>
                      <span className="text-xs text-slate-400 flex items-center gap-1 font-mono">
                        <Clock className="w-3.5 h-3.5 text-cyan-400" /> {t.duration_minutes} Mins
                      </span>
                    </div>

                    <h3 className="text-lg font-bold text-white">{t.title}</h3>
                    <p className="text-xs text-slate-300 flex items-center gap-2">
                      <Briefcase className="w-3.5 h-3.5 text-cyan-400" /> {t.job_title}
                    </p>

                    <div className="flex flex-wrap items-center gap-2 pt-2 text-xs">
                      <span className="px-2.5 py-1 rounded-md bg-white/10 text-slate-200">
                        20 Questions Picked
                      </span>
                      <span className="px-2.5 py-1 rounded-md bg-white/10 text-slate-200">
                        Pass Mark: {t.passing_percentage}%
                      </span>
                    </div>
                  </div>

                  <div className="pt-6 mt-6 border-t border-white/10 flex items-center justify-between">
                    <button
                      onClick={() => handleOpenPreview(t)}
                      className="px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-white/10 hover:bg-white/20 text-white flex items-center gap-1.5"
                    >
                      <Eye className="w-3.5 h-3.5" /> Preview 20 Qs
                    </button>

                    <button
                      onClick={() => handleDeleteTemplate(t.template_id)}
                      className="px-3 py-1.5 rounded-xl text-xs font-semibold text-rose-400 hover:text-rose-300 bg-rose-500/10 hover:bg-rose-500/20"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ================= TAB 4: DRAFT ASSESSMENTS ================= */}
      {activeTab === 'drafts' && (
        <div className="space-y-6">
          <div>
            <h3 className="text-xl font-bold font-heading text-white flex items-center gap-2">
              <FileText className="w-5 h-5 text-amber-400" />
              Draft Assessments
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              In-progress assessments. Complete 20 questions selection to publish them for candidates.
            </p>
          </div>

          {draftTemplates.length === 0 ? (
            <div className="p-12 text-center rounded-2xl glass-card border border-white/10">
              <FileText className="w-12 h-12 text-slate-500 mx-auto mb-3" />
              <h3 className="text-base font-bold text-white mb-1">No draft assessments</h3>
              <p className="text-xs text-slate-400">All created assessments have either been published or not yet started.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {draftTemplates.map((t) => (
                <div
                  key={t.template_id}
                  className="p-6 rounded-3xl glass-card border border-amber-500/30 bg-amber-500/5 flex flex-col justify-between"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-3">
                      <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 uppercase tracking-wider">
                        Draft Incomplete
                      </span>
                      <span className="text-xs text-slate-400 font-mono">
                        {t.duration_minutes} Mins
                      </span>
                    </div>

                    <h3 className="text-lg font-bold text-white">{t.title}</h3>
                    <p className="text-xs text-slate-300 flex items-center gap-2">
                      <Briefcase className="w-3.5 h-3.5 text-cyan-400" /> {t.job_title}
                    </p>

                    <div className="p-3 rounded-xl bg-black/30 border border-white/5 text-xs text-slate-300 flex items-center justify-between">
                      <span>Questions Selected:</span>
                      <span className="font-bold text-amber-400">{t.questions_count} / 20</span>
                    </div>
                  </div>

                  <div className="pt-6 mt-6 border-t border-white/10 flex items-center justify-between">
                    <button
                      onClick={() => handleEditDraft(t)}
                      className="px-4 py-2 rounded-xl text-xs font-bold bg-cyan-500 hover:bg-cyan-400 text-black flex items-center gap-1.5"
                    >
                      <Edit3 className="w-3.5 h-3.5" /> Continue Editing
                    </button>

                    <div className="flex items-center gap-2">
                      {t.questions_count === 20 && (
                        <button
                          onClick={() => handlePublishTemplate(t.template_id)}
                          className="px-3.5 py-2 rounded-xl text-xs font-bold bg-emerald-500 text-black hover:bg-emerald-400"
                        >
                          Publish Now
                        </button>
                      )}
                      <button
                        onClick={() => handleDeleteTemplate(t.template_id)}
                        className="px-3 py-2 rounded-xl text-xs text-rose-400 hover:text-rose-300 bg-rose-500/10"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ================= TAB 5: CANDIDATE ASSESSMENT RESULTS ================= */}
      {activeTab === 'results' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold font-heading text-white flex items-center gap-2">
                <Award className="w-5 h-5 text-purple-400" />
                Candidate Assessment Results
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Real-time scores out of 20, pass/fail status, and complete answer sheet inspections.
              </p>
            </div>
            <button
              onClick={loadAllData}
              className="px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-xs text-slate-300 border border-white/10 flex items-center gap-1.5"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Refresh
            </button>
          </div>

          {candidateResults.length === 0 ? (
            <div className="p-12 text-center rounded-2xl glass-card border border-white/10">
              <Award className="w-12 h-12 text-slate-500 mx-auto mb-3" />
              <h3 className="text-base font-bold text-white mb-1">No candidate assessment attempts recorded</h3>
              <p className="text-xs text-slate-400">When shortlisted candidates complete their 20-question test, results appear here.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {candidateResults.map((res) => {
                const isCompleted = res.status === 'completed';
                const isPassed = res.passed;

                return (
                  <div
                    key={res.assessment_id}
                    className="p-5 rounded-2xl glass-card border border-white/10 flex flex-col md:flex-row md:items-center justify-between gap-4"
                  >
                    <div className="space-y-1.5">
                      <div className="flex items-center gap-2.5 flex-wrap">
                        <h4 className="text-base font-bold text-white">{res.candidate_name}</h4>
                        <span className="text-xs text-slate-400">({res.candidate_email})</span>
                        <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                          isCompleted
                            ? isPassed
                              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                              : 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                            : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                        }`}>
                          {isCompleted ? (isPassed ? 'Passed (Interview Qualified)' : 'Failed / Under Review') : 'Pending Attempt'}
                        </span>
                      </div>

                      <p className="text-xs text-slate-300 flex items-center gap-2">
                        <Briefcase className="w-3.5 h-3.5 text-cyan-400" /> {res.job_title} • {res.title}
                      </p>
                    </div>

                    <div className="flex items-center gap-6 justify-between md:justify-end">
                      {isCompleted ? (
                        <div className="text-right">
                          <span className="text-[10px] uppercase text-slate-400 font-bold block">Score</span>
                          <span className={`text-xl font-black ${isPassed ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {res.score} / {res.total_questions} ({res.percentage}%)
                          </span>
                        </div>
                      ) : (
                        <span className="text-xs text-amber-400 font-semibold">Test Not Started</span>
                      )}

                      {isCompleted && (
                        <button
                          onClick={() => handleInspectResults(res.assessment_id)}
                          className="px-4 py-2 rounded-xl text-xs font-bold bg-white/10 hover:bg-white/20 text-white flex items-center gap-1.5 transition-colors"
                        >
                          <Eye className="w-3.5 h-3.5" /> Inspect 20 Qs Answers
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* ================= MODAL: AI QUESTION GENERATOR ================= */}
      {isAIQuestionModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="glass-card p-6 md:p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-purple-500/30 rounded-3xl shadow-2xl space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-white/10">
              <div>
                <span className="text-xs font-bold uppercase text-purple-400 tracking-wider flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                  SkillSphere AI Studio
                </span>
                <h3 className="text-xl font-bold text-white">Generate Questions with AI</h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Generates technical MCQs tailored to the role using Gemini AI or the Question Bank engine.
                </p>
              </div>
              <button
                onClick={() => {
                  setIsAIQuestionModalOpen(false);
                  setAiGeneratedQuestions([]);
                }}
                className="p-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Input Controls */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Target Job Role</label>
                <input
                  type="text"
                  value={aiRole}
                  onChange={(e) => setAiRole(e.target.value)}
                  placeholder="e.g. Senior React Developer"
                  className="w-full glass-input px-3 py-2 rounded-xl text-xs text-white"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Technology Focus</label>
                <select
                  value={aiTech}
                  onChange={(e) => setAiTech(e.target.value)}
                  className="w-full bg-dark-850 border border-white/10 text-white rounded-xl px-3 py-2 text-xs"
                >
                  {TECHNOLOGIES.filter((t) => t !== 'All').map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Difficulty Level</label>
                <select
                  value={aiDiff}
                  onChange={(e) => setAiDiff(e.target.value)}
                  className="w-full bg-dark-850 border border-white/10 text-white rounded-xl px-3 py-2 text-xs"
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Questions Count</label>
                <select
                  value={aiCount}
                  onChange={(e) => setAiCount(e.target.value)}
                  className="w-full bg-dark-850 border border-white/10 text-white rounded-xl px-3 py-2 text-xs"
                >
                  <option value="3">3 Questions</option>
                  <option value="5">5 Questions (Recommended)</option>
                  <option value="10">10 Questions</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end">
              <button
                type="button"
                disabled={aiGenerating}
                onClick={handleGenerateAIQuestions}
                className={`px-5 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 transition-all ${
                  aiGenerating
                    ? 'bg-purple-500/20 text-purple-300 cursor-not-allowed'
                    : 'bg-gradient-to-r from-purple-500 to-cyan-500 text-white hover:brightness-110 shadow-lg shadow-purple-500/20'
                }`}
              >
                {aiGenerating ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Generating Questions with AI...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Generate MCQs Now</span>
                  </>
                )}
              </button>
            </div>

            {/* Generated Questions Preview */}
            {aiGeneratedQuestions.length > 0 && (
              <div className="space-y-4 pt-4 border-t border-white/10">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold uppercase text-emerald-400 tracking-wider">
                    Generated {aiGeneratedQuestions.length} Questions:
                  </h4>
                  <button
                    type="button"
                    disabled={savingQuestion}
                    onClick={handleAddAIQuestionsToBank}
                    className="px-4 py-2 rounded-xl text-xs font-bold bg-emerald-500 text-black hover:bg-emerald-400 flex items-center gap-1.5 shadow-lg shadow-emerald-500/20"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Add All {aiGeneratedQuestions.length} to Question Bank</span>
                  </button>
                </div>

                <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
                  {aiGeneratedQuestions.map((q, idx) => (
                    <div key={idx} className="p-3.5 rounded-xl bg-black/40 border border-white/10 space-y-2 text-xs">
                      <p className="font-bold text-white">Q{idx + 1}: {q.question_text}</p>
                      <div className="grid grid-cols-2 gap-1.5">
                        {q.options.map((opt, oIdx) => (
                          <div
                            key={oIdx}
                            className={`p-2 rounded-lg border text-[11px] ${
                              opt === q.correct_answer
                                ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-300 font-semibold'
                                : 'bg-white/5 border-white/5 text-slate-300'
                            }`}
                          >
                            {opt}
                          </div>
                        ))}
                      </div>
                      {q.explanation && (
                        <p className="text-[11px] text-slate-400 bg-white/5 p-2 rounded">
                          <strong>Explanation:</strong> {q.explanation}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ================= MODAL: CREATE / EDIT QUESTION ================= */}
      {isCreateQuestionOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="glass-card p-6 md:p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-white/15 rounded-3xl shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-white/10 mb-4">
              <div>
                <span className="text-xs font-bold uppercase text-cyan-400 tracking-wider">Recruiter Question Studio</span>
                <h3 className="text-xl font-bold text-white">
                  {editingQuestion ? 'Edit Technical Question' : 'Create New MCQ Question'}
                </h3>
              </div>
              <button
                onClick={() => setIsCreateQuestionOpen(false)}
                className="p-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveQuestion} className="space-y-4 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Technology / Subject</label>
                  <input
                    type="text"
                    required
                    value={qTech}
                    onChange={(e) => setQTech(e.target.value)}
                    placeholder="e.g. Python, React, SQL"
                    className="w-full glass-input px-3 py-2 rounded-xl text-xs text-white"
                  />
                </div>

                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Difficulty</label>
                  <select
                    value={qDiff}
                    onChange={(e) => setQDiff(e.target.value)}
                    className="w-full bg-dark-850 border border-white/10 text-white rounded-xl px-3 py-2 text-xs"
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Job Opening (Optional)</label>
                  <select
                    value={qJobId}
                    onChange={(e) => setQJobId(e.target.value)}
                    className="w-full bg-dark-850 border border-white/10 text-white rounded-xl px-3 py-2 text-xs"
                  >
                    <option value="">General Bank</option>
                    {jobs.map((j) => (
                      <option key={j.job_id} value={j.job_id}>{j.title}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Question Text</label>
                <textarea
                  required
                  rows={3}
                  value={qText}
                  onChange={(e) => setQText(e.target.value)}
                  placeholder="Enter the complete technical question formulation..."
                  className="w-full glass-input p-3 rounded-xl text-xs text-white leading-relaxed"
                />
              </div>

              {/* 4 MCQ Options */}
              <div className="space-y-2 pt-2">
                <label className="block text-slate-300 font-semibold">Four Multiple Choice Options</label>

                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="w-7 h-7 rounded-lg bg-white/10 flex items-center justify-center font-bold font-mono text-cyan-300 shrink-0">A</span>
                    <input
                      type="text"
                      required
                      value={qOptA}
                      onChange={(e) => setQOptA(e.target.value)}
                      placeholder="Option A"
                      className="flex-1 glass-input px-3 py-2 rounded-xl text-xs text-white"
                    />
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="w-7 h-7 rounded-lg bg-white/10 flex items-center justify-center font-bold font-mono text-cyan-300 shrink-0">B</span>
                    <input
                      type="text"
                      required
                      value={qOptB}
                      onChange={(e) => setQOptB(e.target.value)}
                      placeholder="Option B"
                      className="flex-1 glass-input px-3 py-2 rounded-xl text-xs text-white"
                    />
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="w-7 h-7 rounded-lg bg-white/10 flex items-center justify-center font-bold font-mono text-cyan-300 shrink-0">C</span>
                    <input
                      type="text"
                      required
                      value={qOptC}
                      onChange={(e) => setQOptC(e.target.value)}
                      placeholder="Option C"
                      className="flex-1 glass-input px-3 py-2 rounded-xl text-xs text-white"
                    />
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="w-7 h-7 rounded-lg bg-white/10 flex items-center justify-center font-bold font-mono text-cyan-300 shrink-0">D</span>
                    <input
                      type="text"
                      required
                      value={qOptD}
                      onChange={(e) => setQOptD(e.target.value)}
                      placeholder="Option D"
                      className="flex-1 glass-input px-3 py-2 rounded-xl text-xs text-white"
                    />
                  </div>
                </div>
              </div>

              {/* Correct Answer Selector */}
              <div className="pt-2">
                <label className="block text-slate-300 font-semibold mb-1">Designated Correct Answer</label>
                <div className="flex items-center gap-3">
                  {['A', 'B', 'C', 'D'].map((letter) => (
                    <label key={letter} className="flex items-center gap-1.5 cursor-pointer">
                      <input
                        type="radio"
                        name="correctAnswer"
                        value={letter}
                        checked={qCorrect === letter}
                        onChange={(e) => setQCorrect(e.target.value)}
                        className="text-cyan-500 focus:ring-cyan-400"
                      />
                      <span className="font-bold text-white">Option {letter}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Technical Explanation (Optional)</label>
                <textarea
                  rows={2}
                  value={qExplanation}
                  onChange={(e) => setQExplanation(e.target.value)}
                  placeholder="Explain why this answer is correct (shown to candidate post-evaluation)..."
                  className="w-full glass-input p-2.5 rounded-xl text-xs text-white"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-white/10">
                <button
                  type="button"
                  onClick={() => setIsCreateQuestionOpen(false)}
                  className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-slate-300 text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingQuestion}
                  className="px-6 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black text-xs font-bold shadow-lg shadow-cyan-500/20"
                >
                  {savingQuestion ? 'Saving...' : editingQuestion ? 'Update Question' : 'Save to Question Bank'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ================= MODAL: IMPORT FROM QUESTION LIBRARY ================= */}
      {isImportLibraryOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="glass-card p-6 md:p-8 max-w-md w-full border border-white/15 rounded-3xl shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div>
                <span className="text-xs font-bold uppercase text-cyan-400 tracking-wider">Question Library</span>
                <h3 className="text-lg font-bold text-white">Import Curated Questions</h3>
              </div>
              <button
                onClick={() => setIsImportLibraryOpen(false)}
                className="p-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              Pull verified technical questions from SkillSphere's standard library directly into your own question bank.
            </p>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Select Technology Domain</label>
                <select
                  value={importTech}
                  onChange={(e) => setImportTech(e.target.value)}
                  className="w-full bg-dark-850 border border-white/10 text-white rounded-xl px-3 py-2 text-xs"
                >
                  <option value="Python">Python (FastAPI, asyncio, GIL, generators)</option>
                  <option value="React">React (Hooks, Virtual DOM, state management)</option>
                  <option value="Fullstack MERN">Full-Stack MERN (Node, Express, MongoDB)</option>
                  <option value="Java">Java (JVM, Spring Boot, multithreading)</option>
                  <option value="Cloud DevOps">Cloud & DevOps (Docker, Kubernetes, AWS, CI/CD)</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Number of Questions to Import</label>
                <input
                  type="number"
                  min="5"
                  max="35"
                  value={importCount}
                  onChange={(e) => setImportCount(e.target.value)}
                  className="w-full glass-input px-3 py-2 rounded-xl text-xs text-white"
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-white/10">
              <button
                onClick={() => setIsImportLibraryOpen(false)}
                className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-slate-300 text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                disabled={importing}
                onClick={handleImportFromLibrary}
                className="px-6 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black text-xs font-bold shadow-lg shadow-cyan-500/20"
              >
                {importing ? 'Importing Questions...' : 'Import to My Bank'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ================= MODAL: PREVIEW 20-QUESTION TEMPLATE ================= */}
      {previewTemplate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="glass-card p-6 md:p-8 max-w-3xl w-full max-h-[90vh] overflow-y-auto border border-white/15 rounded-3xl shadow-2xl space-y-6">
            <div className="flex items-start justify-between pb-4 border-b border-white/10">
              <div>
                <span className="text-xs font-bold uppercase text-emerald-400 tracking-wider">Assessment Preview</span>
                <h3 className="text-2xl font-black text-white">{previewTemplate.title}</h3>
                <p className="text-xs text-slate-400 mt-1">
                  Job: {previewTemplate.job_title} • {previewTemplate.tech_stack} • {previewTemplate.duration_minutes} Mins • {previewTemplate.questions_count} Questions
                </p>
              </div>
              <button
                onClick={() => setPreviewTemplate(null)}
                className="p-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              {(previewTemplate.questions || []).map((q, qIdx) => (
                <div key={q.question_id} className="p-4 rounded-xl bg-dark-850/80 border border-white/10 space-y-2 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-cyan-400">Q{qIdx + 1}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] bg-white/10 text-slate-300 font-bold uppercase">
                      {q.difficulty}
                    </span>
                  </div>
                  <p className="font-bold text-white text-sm leading-relaxed">{q.question_text}</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
                    {(q.options || []).map((opt, oIdx) => (
                      <div
                        key={oIdx}
                        className={`p-2 rounded-lg border ${
                          opt === q.correct_answer
                            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300 font-bold'
                            : 'bg-black/20 border-white/5 text-slate-300'
                        }`}
                      >
                        {String.fromCharCode(65 + oIdx)}. {opt}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-end pt-4 border-t border-white/10">
              <button
                onClick={() => setPreviewTemplate(null)}
                className="px-6 py-2.5 rounded-xl bg-cyan-500 text-black font-bold text-xs"
              >
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ================= MODAL: INSPECT CANDIDATE RESULTS ================= */}
      {inspectResultId && inspectResultData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="glass-card p-6 md:p-8 max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-white/15 rounded-3xl shadow-2xl space-y-6">
            <div className="flex items-start justify-between pb-4 border-b border-white/10">
              <div>
                <span className="text-xs font-bold uppercase text-purple-400 tracking-wider">Candidate Test Evaluation</span>
                <h3 className="text-2xl font-black text-white">{inspectResultData.candidate_name}</h3>
                <p className="text-xs text-slate-400 mt-1">
                  {inspectResultData.title} • {inspectResultData.job_title}
                </p>
              </div>

              <div className="text-right">
                <span className="text-xs text-slate-400 block font-semibold">Final Score</span>
                <span className={`text-2xl font-black ${inspectResultData.passed ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {inspectResultData.score}/{inspectResultData.total_questions} ({inspectResultData.percentage}%)
                </span>
                <span className="text-[10px] text-slate-400 block">Pass Mark: {inspectResultData.passing_percentage}%</span>
              </div>
            </div>

            <div className="space-y-3">
              {(inspectResultData.breakdown || []).map((q, idx) => (
                <div
                  key={q.question_id || idx}
                  className={`p-4 rounded-xl border text-xs ${
                    q.is_correct ? 'bg-emerald-500/5 border-emerald-500/20' : 'bg-rose-500/5 border-rose-500/20'
                  }`}
                >
                  <p className="font-bold text-white mb-2">Q{idx + 1}: {q.question_text}</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-2">
                    <div className={`p-2 rounded-lg border ${q.is_correct ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-rose-500/10 border-rose-500/30 text-rose-300'}`}>
                      <span className="font-bold block text-[10px]">Candidate Answer:</span>
                      <span>{q.candidate_answer || '(Unanswered)'}</span>
                    </div>
                    <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
                      <span className="font-bold block text-[10px]">Correct Answer:</span>
                      <span>{q.correct_answer}</span>
                    </div>
                  </div>
                  {q.explanation && (
                    <p className="text-[11px] text-slate-400 bg-black/30 p-2 rounded border border-white/5 font-mono">
                      {q.explanation}
                    </p>
                  )}
                </div>
              ))}
            </div>

            <div className="flex justify-end pt-4 border-t border-white/10">
              <button
                onClick={() => {
                  setInspectResultId(null);
                  setInspectResultData(null);
                }}
                className="px-6 py-2.5 rounded-xl bg-cyan-500 text-black font-bold text-xs"
              >
                Close Answer Sheet
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
