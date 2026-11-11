import React from 'react';

export default function RadialGauge({ score, size = 100, strokeWidth = 8 }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const normalizedScore = Math.min(100, Math.max(0, score || 0));
  const strokeDashoffset = circumference - (normalizedScore / 100) * circumference;

  let strokeColor = '#00f5ff'; // cyan
  let glowColor = 'rgba(0, 245, 255, 0.4)';
  if (normalizedScore >= 80) {
    strokeColor = '#10b981'; // emerald
    glowColor = 'rgba(16, 185, 129, 0.4)';
  } else if (normalizedScore < 50) {
    strokeColor = '#f59e0b'; // amber
    glowColor = 'rgba(245, 158, 11, 0.4)';
  }

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgba(255, 255, 255, 0.08)"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={strokeColor}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          fill="transparent"
          style={{
            transition: 'stroke-dashoffset 1s ease-in-out',
            filter: `drop-shadow(0 0 6px ${glowColor})`,
          }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
        <span className="text-xl font-bold font-heading text-white">{Math.round(normalizedScore)}%</span>
        <span className="text-[10px] uppercase tracking-wider text-slate-400 font-medium">Match</span>
      </div>
    </div>
  );
}
