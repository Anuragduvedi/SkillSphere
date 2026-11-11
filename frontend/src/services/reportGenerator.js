export function generateResumeAnalysisReport(analysis, candidateName = 'Alex Rivera') {
  if (!analysis) return;

  const printWindow = window.open('', '_blank');
  if (!printWindow) {
    alert('Please allow popups to download the analysis report.');
    return;
  }

  const html = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>SkillSphere Executive Match Analysis - ${analysis.job_title}</title>
      <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Space+Grotesk:wght@600;700&display=swap');
        
        body {
          font-family: 'Plus Jakarta Sans', sans-serif;
          background: #090D18;
          color: #f1f5f9;
          margin: 0;
          padding: 40px;
          line-height: 1.5;
        }
        
        .container {
          max-width: 800px;
          margin: 0 auto;
          background: #0F172A;
          border: 1px solid rgba(255, 255, 255, 0.15);
          border-radius: 20px;
          padding: 40px;
          box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        }

        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
          padding-bottom: 24px;
          margin-bottom: 30px;
        }

        .brand {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 24px;
          font-weight: 800;
          color: #ffffff;
        }
        .brand span { color: #00f5ff; }

        .badge {
          display: inline-block;
          background: rgba(0, 245, 255, 0.1);
          color: #00f5ff;
          border: 1px solid rgba(0, 245, 255, 0.3);
          padding: 4px 12px;
          border-radius: 9999px;
          font-size: 11px;
          font-weight: 700;
          text-transform: uppercase;
        }

        .hero-score {
          display: flex;
          align-items: center;
          justify-content: space-between;
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 16px;
          padding: 24px;
          margin-bottom: 30px;
        }

        .score-circle {
          width: 90px;
          height: 90px;
          border-radius: 50%;
          border: 6px solid #10b981;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
        }

        .score-val {
          font-size: 26px;
          font-weight: 800;
          color: #ffffff;
        }

        .section-title {
          font-size: 14px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: #94a3b8;
          margin-top: 24px;
          margin-bottom: 12px;
        }

        .skill-grid {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-bottom: 20px;
        }

        .skill-pill {
          padding: 6px 14px;
          border-radius: 8px;
          font-size: 12px;
          font-weight: 600;
        }

        .pill-matched {
          background: rgba(16, 185, 129, 0.15);
          color: #34d399;
          border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .pill-missing {
          background: rgba(245, 158, 11, 0.15);
          color: #fbbf24;
          border: 1px solid rgba(245, 158, 11, 0.3);
        }

        .rec-box {
          background: rgba(0, 245, 255, 0.05);
          border: 1px solid rgba(0, 245, 255, 0.2);
          border-radius: 12px;
          padding: 20px;
          font-size: 13px;
          color: #cbd5e1;
          line-height: 1.6;
        }

        .footer {
          margin-top: 40px;
          border-top: 1px solid rgba(255, 255, 255, 0.1);
          padding-top: 20px;
          display: flex;
          justify-content: space-between;
          font-size: 11px;
          color: #64748b;
        }

        @media print {
          body { background: white; color: black; padding: 0; }
          .container { border: none; box-shadow: none; background: white; color: black; max-width: 100%; }
          .brand { color: black; }
          .brand span { color: #0284c7; }
          .hero-score { background: #f8fafc; border: 1px solid #e2e8f0; color: black; }
          .score-val { color: black; }
          .rec-box { background: #f0fdfa; border: 1px solid #99f6e4; color: #0f172a; }
          .pill-matched { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
          .pill-missing { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <div>
            <div class="brand">Skill<span>Sphere</span></div>
            <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">Career Intelligence & Resume Match Analysis</div>
          </div>
          <div class="badge">Verified Telemetry Report</div>
        </div>

        <div class="hero-score">
          <div>
            <h2 style="margin: 0 0 6px 0; font-size: 20px; color: #ffffff;">${analysis.job_title}</h2>
            <div style="font-size: 13px; color: #94a3b8;">
              Company: <strong style="color: #ffffff;">${analysis.company_name || 'Enterprise Employer'}</strong> | Candidate: <strong style="color: #ffffff;">${candidateName}</strong>
            </div>
            <div style="font-size: 12px; color: #64748b; margin-top: 4px;">
              Generated: ${new Date().toLocaleDateString()} at ${new Date().toLocaleTimeString()}
            </div>
          </div>
          <div class="score-circle">
            <div class="score-val">${Math.round(analysis.match_score)}%</div>
            <div style="font-size: 9px; text-transform: uppercase; color: #94a3b8; font-weight: 700;">Fit Score</div>
          </div>
        </div>

        <div class="section-title">Verified Core Competencies (${analysis.matched_skills.length})</div>
        <div class="skill-grid">
          ${analysis.matched_skills.map(s => `<div class="skill-pill pill-matched">✓ ${s}</div>`).join('')}
        </div>

        <div class="section-title">Identified Skill Gaps (${analysis.missing_skills.length})</div>
        <div class="skill-grid">
          ${analysis.missing_skills.length > 0 
            ? analysis.missing_skills.map(s => `<div class="skill-pill pill-missing">! ${s}</div>`).join('') 
            : '<div style="font-size: 13px; color: #10b981;">100% of prerequisites satisfied</div>'}
        </div>

        <div class="section-title">Explainable Recommendation</div>
        <div class="rec-box">
          ${analysis.recommendations}
        </div>

        <div class="footer">
          <div>SkillSphere Automated Evaluation Engine • Version 2.0</div>
          <div>Confidential Career Telemetry Report</div>
        </div>
      </div>
      <script>
        window.onload = function() {
          window.print();
        };
      </script>
    </body>
    </html>
  `;

  printWindow.document.open();
  printWindow.document.write(html);
  printWindow.document.close();
}
