import React, { useState, useRef } from 'react';
import { 
  Upload, 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  X, 
  Loader2, 
  Plus, 
  Sparkles,
  ArrowRight,
  RefreshCw
} from 'lucide-react';
import { resumeAPI } from '../services/api';
import { useToast } from '../context/ToastContext';
import { useAuth } from '../context/AuthContext';

export default function ResumeUploadModal({ isOpen, onClose, onProfileUpdated }) {
  const { showToast } = useToast();
  const { refreshProfile } = useAuth();
  
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [ocrResult, setOcrResult] = useState(null);

  // Editable fields after extraction
  const [editableName, setEditableName] = useState('');
  const [editablePhone, setEditablePhone] = useState('');
  const [editableEducation, setEditableEducation] = useState('');
  const [editableExperience, setEditableExperience] = useState('');
  const [skillsList, setSkillsList] = useState([]);
  const [newSkillInput, setNewSkillInput] = useState('');

  const inputRef = useRef(null);

  if (!isOpen) return null;

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    const validExtensions = ['.pdf', '.jpg', '.jpeg', '.png'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!validExtensions.includes(ext)) {
      showToast(`Invalid file type (${ext}). Please upload a PDF, JPG, or PNG resume.`, 'error');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      showToast(`File size (${(file.size / (1024*1024)).toFixed(1)}MB) exceeds 10MB limit.`, 'error');
      return;
    }

    setSelectedFile(file);
    processResume(file);
  };

  const processResume = async (file) => {
    setIsProcessing(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await resumeAPI.upload(formData);
      const data = res.data;
      setOcrResult(data);
      
      // Populate editable fields
      setEditableName(data.extracted_name || '');
      setEditablePhone(data.extracted_phone || '');
      setEditableEducation(data.extracted_education || '');
      setEditableExperience(data.extracted_experience || '');
      setSkillsList(data.extracted_skills || []);

      showToast('Resume uploaded and OCR extraction completed successfully!', 'success');
    } catch (err) {
      console.error('OCR processing error:', err);
      const detail = err.response?.data?.detail || 'Failed to process resume OCR.';
      showToast(detail, 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAddSkill = (e) => {
    e.preventDefault();
    const clean = newSkillInput.trim();
    if (clean && !skillsList.some((s) => s.toLowerCase() === clean.toLowerCase())) {
      setSkillsList([...skillsList, clean]);
      setNewSkillInput('');
    }
  };

  const handleRemoveSkill = (skillToRemove) => {
    setSkillsList(skillsList.filter((s) => s !== skillToRemove));
  };

  const handleSaveToProfile = async () => {
    setIsSaving(true);
    try {
      await resumeAPI.updateProfile({
        name: editableName,
        phone: editablePhone,
        education: editableEducation,
        experience: editableExperience,
        skills: skillsList,
      });

      await refreshProfile();
      if (onProfileUpdated) onProfileUpdated();
      showToast('Candidate profile updated with OCR extracted details!', 'success');
      onClose();
    } catch (err) {
      console.error('Error saving profile:', err);
      showToast('Failed to save profile changes.', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const resetAll = () => {
    setSelectedFile(null);
    setOcrResult(null);
    setSkillsList([]);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md overflow-y-auto">
      <div className="relative w-full max-w-2xl bg-dark-850/95 border border-white/20 rounded-2xl shadow-2xl shadow-cyan-950/40 p-6 md:p-8 my-8 text-slate-100">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl bg-white/5 border border-white/10 text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-xl font-bold font-heading text-white">Smart Resume OCR Extraction</h2>
            <p className="text-xs text-slate-400">PDF, JPG, PNG up to 10MB • Optical text recognition engine</p>
          </div>
        </div>

        {/* Phase 1: Upload Dropzone */}
        {!ocrResult && !isProcessing && (
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => inputRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-300 ${
              dragActive 
                ? 'border-cyan-400 bg-cyan-950/30 shadow-neon-cyan/20' 
                : 'border-white/15 bg-white/[0.02] hover:border-cyan-500/50 hover:bg-white/[0.04]'
            }`}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".pdf,.png,.jpg,.jpeg"
              onChange={handleChange}
              className="hidden"
            />
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-tr from-cyan-500/20 to-purple-500/20 border border-white/10 flex items-center justify-center">
              <Upload className="w-8 h-8 text-cyan-400" />
            </div>
            <h3 className="text-base font-semibold text-white mb-1">Drag and drop resume here</h3>
            <p className="text-xs text-slate-400 mb-4">or click to browse from device</p>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-[11px] text-slate-300">
              <FileText className="w-3.5 h-3.5 text-cyan-400" />
              Supported: PDF, JPG, JPEG, PNG (Max 10MB)
            </div>
          </div>
        )}

        {/* Phase 2: Processing Loader */}
        {isProcessing && (
          <div className="py-16 text-center space-y-4">
            <Loader2 className="w-12 h-12 text-cyan-400 animate-spin mx-auto" />
            <h3 className="text-lg font-bold font-heading text-white">Extracting Resume Data</h3>
            <p className="text-xs text-slate-400 max-w-sm mx-auto leading-relaxed">
              Applying image contrast filters, running OCR pipeline, and parsing contact metadata and competencies...
            </p>
          </div>
        )}

        {/* Phase 3: Review and Edit Extracted Fields */}
        {ocrResult && (
          <div className="space-y-5 animate-in fade-in duration-300">
            <div className="flex items-center justify-between p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/30">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-cyan-400" />
                <span className="text-xs font-semibold text-cyan-200">
                  OCR Text Parsed: {ocrResult.file_name}
                </span>
              </div>
              <button
                onClick={resetAll}
                className="text-xs text-slate-400 hover:text-white flex items-center gap-1"
              >
                <RefreshCw className="w-3 h-3" /> Re-upload
              </button>
            </div>

            <p className="text-xs text-slate-400">
              Review and edit the extracted information below before saving to your profile:
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Extracted Name</label>
                <input
                  type="text"
                  value={editableName}
                  onChange={(e) => setEditableName(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-xl glass-input"
                  placeholder="Candidate Name"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Phone Number</label>
                <input
                  type="text"
                  value={editablePhone}
                  onChange={(e) => setEditablePhone(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-xl glass-input"
                  placeholder="+1 (555) 000-0000"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Education</label>
              <input
                type="text"
                value={editableEducation}
                onChange={(e) => setEditableEducation(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-xl glass-input"
                placeholder="Degree, Major, Institution"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Experience Summary</label>
              <textarea
                rows={2}
                value={editableExperience}
                onChange={(e) => setEditableExperience(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-xl glass-input"
                placeholder="Years of experience and key focus areas"
              />
            </div>

            {/* Extracted Skills Badges */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-2">
                Identified Competencies & Skills ({skillsList.length})
              </label>
              <div className="flex flex-wrap gap-2 mb-3 max-h-36 overflow-y-auto p-2 rounded-xl bg-dark-900/60 border border-white/10">
                {skillsList.map((skill) => (
                  <span
                    key={skill}
                    className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                  >
                    {skill}
                    <button
                      onClick={() => handleRemoveSkill(skill)}
                      className="hover:text-rose-400"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
                {skillsList.length === 0 && (
                  <p className="text-xs text-slate-500">No skills identified. Add custom tags below.</p>
                )}
              </div>

              {/* Add custom skill tag */}
              <form onSubmit={handleAddSkill} className="flex gap-2">
                <input
                  type="text"
                  value={newSkillInput}
                  onChange={(e) => setNewSkillInput(e.target.value)}
                  placeholder="Add skill tag (e.g., Docker, GraphQL)..."
                  className="flex-1 px-3 py-1.5 text-xs rounded-xl glass-input"
                />
                <button
                  type="submit"
                  className="px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-xs font-medium text-white flex items-center gap-1 transition-colors"
                >
                  <Plus className="w-3.5 h-3.5" /> Add
                </button>
              </form>
            </div>

            {/* Action buttons */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={isSaving}
                onClick={handleSaveToProfile}
                className="px-5 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-lg shadow-cyan-500/25 hover:brightness-110 flex items-center gap-2 transition-all"
              >
                {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
                Save & Update Candidate Profile
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
