import React from 'react';
import { motion } from 'framer-motion';
import { MdSentimentSatisfied, MdSentimentDissatisfied, MdSentimentNeutral } from 'react-icons/md';
import ConfidenceBar from './ConfidenceBar';

const SentimentCard = ({ result }) => {
  if (!result) return null;

  const { text, sentiment, confidence, probabilities, key_words } = result;

  // Sentiment mapping for icons, colors, descriptions
  const sentimentMap = {
    Positive: {
      color: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20',
      textColor: 'text-emerald-500 dark:text-emerald-400',
      icon: MdSentimentSatisfied,
      gradient: 'from-emerald-500/20 to-teal-500/20',
      glow: 'shadow-emerald-500/10',
      bgGlow: 'bg-emerald-500'
    },
    Negative: {
      color: 'text-rose-500 bg-rose-500/10 border-rose-500/20',
      textColor: 'text-rose-500 dark:text-rose-400',
      icon: MdSentimentDissatisfied,
      gradient: 'from-rose-500/20 to-orange-500/20',
      glow: 'shadow-rose-500/10',
      bgGlow: 'bg-rose-500'
    },
    Neutral: {
      color: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
      textColor: 'text-amber-500 dark:text-amber-400',
      icon: MdSentimentNeutral,
      gradient: 'from-amber-500/20 to-yellow-500/20',
      glow: 'shadow-amber-500/10',
      bgGlow: 'bg-amber-500'
    }
  };

  const currentSentiment = sentimentMap[sentiment] || sentimentMap.Neutral;
  const SentimentIcon = currentSentiment.icon;

  // Highlight words function
  const renderHighlightedText = () => {
    if (!text) return '';
    const posWords = key_words?.positive || [];
    const negWords = key_words?.negative || [];
    
    if (posWords.length === 0 && negWords.length === 0) {
      return text;
    }

    // Split text into tokens while preserving punctuation/whitespace
    // This regex splits on word boundaries
    const tokens = text.split(/(\s+)/);
    
    return tokens.map((token, index) => {
      // Clean token to check matching
      const cleanToken = token.toLowerCase().replace(/[^\w]/g, '');
      
      const isPositive = posWords.some(w => cleanToken === w.toLowerCase() || w.toLowerCase().includes(cleanToken) && cleanToken.length > 2);
      const isNegative = negWords.some(w => cleanToken === w.toLowerCase() || w.toLowerCase().includes(cleanToken) && cleanToken.length > 2);

      if (isPositive && cleanToken) {
        return (
          <span 
            key={index} 
            className="bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 px-1 py-0.5 rounded font-semibold text-sm inline-block transition-colors"
          >
            {token}
          </span>
        );
      } else if (isNegative && cleanToken) {
        return (
          <span 
            key={index} 
            className="bg-rose-500/15 text-rose-600 dark:text-rose-400 border border-rose-500/20 px-1 py-0.5 rounded font-semibold text-sm inline-block transition-colors"
          >
            {token}
          </span>
        );
      }
      return token;
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className={`relative w-full overflow-hidden rounded-2xl border bg-white p-6 shadow-xl ${currentSentiment.glow} dark:bg-slate-900 dark:border-slate-800 transition-all bg-gradient-to-br from-white via-white to-transparent`}
    >
      {/* Background Gradient Accent */}
      <div className={`absolute -right-20 -top-20 h-40 w-40 rounded-full bg-gradient-to-br ${currentSentiment.gradient} blur-3xl opacity-60 pointer-events-none`} />

      {/* Grid Container */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
        {/* Left Side: Score & Label Badge with Micro-animations */}
        <motion.div 
          whileHover={{ scale: 1.02 }}
          transition={{ type: 'spring', stiffness: 300, damping: 15 }}
          className="flex flex-col items-center justify-center p-4 border rounded-xl bg-slate-50/50 dark:bg-slate-800/40 dark:border-slate-800 text-center shadow-sm"
        >
          <div className="relative flex items-center justify-center">
            {/* Animated Ring */}
            <div 
              style={{ animation: 'spin 10s linear infinite' }}
              className={`absolute w-16 h-16 rounded-full border-2 border-dashed opacity-30 ${currentSentiment.textColor}`} 
            />
            <motion.div
              animate={{ scale: [1, 1.08, 1] }}
              transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
            >
              <SentimentIcon size={44} className={currentSentiment.textColor} />
            </motion.div>
          </div>
          <h4 className="mt-3 text-xs font-semibold text-slate-400 uppercase tracking-widest leading-none">Detected Sentiment</h4>
          <h3 className={`text-2xl font-bold mt-2 flex items-center justify-center gap-1.5 ${currentSentiment.textColor}`}>
            <span className={`w-2.5 h-2.5 rounded-full ${currentSentiment.bgGlow} animate-pulse`} />
            {sentiment}
          </h3>
          <div className="mt-4 px-3 py-1 rounded-full bg-slate-200/50 dark:bg-slate-800 border dark:border-slate-700 text-xs font-bold text-slate-500 dark:text-slate-400 shadow-sm">
            {confidence}% Confidence
          </div>
        </motion.div>

        {/* Right Side (Span 2): Highlighted Text & Probability Distribution */}
        <div className="md:col-span-2 space-y-5">
          {/* Highlighted text block */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Input Text & Influencing Words</h4>
            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/20 dark:border dark:border-slate-800 text-sm leading-relaxed text-slate-700 dark:text-slate-300 font-medium">
              {renderHighlightedText()}
            </div>
            {(key_words?.positive?.length > 0 || key_words?.negative?.length > 0) && (
              <p className="text-[11px] text-slate-400 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" /> Positive indicator words and 
                <span className="w-1.5 h-1.5 rounded-full bg-rose-500" /> Negative indicator words highlighted.
              </p>
            )}
          </div>

          {/* Probability stacked bar */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Probability Distribution</h4>
            <ConfidenceBar probabilities={probabilities} />
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default SentimentCard;
