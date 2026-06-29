import React from 'react';

const ConfidenceBar = ({ probabilities }) => {
  if (!probabilities) return null;

  const { positive = 0, negative = 0, neutral = 0 } = probabilities;

  // Safe checks to avoid rendering issues
  const posVal = parseFloat(positive) || 0;
  const negVal = parseFloat(negative) || 0;
  const neuVal = parseFloat(neutral) || 0;

  return (
    <div className="space-y-2.5">
      {/* Visual Stacked Progress Bar */}
      <div className="w-full h-4 flex rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden border dark:border-slate-800 shadow-inner">
        {/* Positive (Emerald) */}
        {posVal > 0 && (
          <div 
            style={{ width: `${posVal}%` }} 
            className="h-full bg-emerald-500 bg-gradient-to-r from-emerald-500 to-teal-500 transition-all duration-500 ease-out"
            title={`Positive: ${posVal}%`}
          />
        )}
        
        {/* Neutral (Amber) */}
        {neuVal > 0 && (
          <div 
            style={{ width: `${neuVal}%` }} 
            className="h-full bg-amber-500 bg-gradient-to-r from-amber-500 to-yellow-500 transition-all duration-500 ease-out"
            title={`Neutral: ${neuVal}%`}
          />
        )}

        {/* Negative (Rose) */}
        {negVal > 0 && (
          <div 
            style={{ width: `${negVal}%` }} 
            className="h-full bg-rose-500 bg-gradient-to-r from-rose-500 to-orange-500 transition-all duration-500 ease-out"
            title={`Negative: ${negVal}%`}
          />
        )}
      </div>

      {/* Percentage Indicators */}
      <div className="flex flex-wrap items-center justify-between text-xs gap-3">
        <div className="flex items-center gap-1.5 font-semibold text-emerald-600 dark:text-emerald-400">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
          <span>Positive: {posVal}%</span>
        </div>

        <div className="flex items-center gap-1.5 font-semibold text-amber-600 dark:text-amber-400">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
          <span>Neutral: {neuVal}%</span>
        </div>

        <div className="flex items-center gap-1.5 font-semibold text-rose-600 dark:text-rose-400">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
          <span>Negative: {negVal}%</span>
        </div>
      </div>
    </div>
  );
};

export default ConfidenceBar;
