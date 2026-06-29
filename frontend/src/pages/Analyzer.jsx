import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { analyzerAPI } from '../api';
import SentimentCard from '../components/SentimentCard';
import { MdSend, MdClear, MdAutoFixHigh } from 'react-icons/md';

const Analyzer = () => {
  const [inputText, setInputText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);

  const sampleTexts = [
    "This platform is absolutely amazing! The interface is so fast and clean.",
    "Customer service was incredibly rude and delayed my order by three weeks. Terrible.",
    "The product is decent, does what it says. Nothing special though.",
  ];

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!inputText.trim()) {
      toast.error('Please enter some text to analyze.');
      return;
    }

    setIsAnalyzing(true);
    setResult(null); // Clear previous result for animated entrance
    
    try {
      const data = await analyzerAPI.analyzeText(inputText);
      // Wait a tiny bit for premium visual feel
      setTimeout(() => {
        setResult(data);
        setIsAnalyzing(false);
        toast.success('Analysis complete!');
      }, 600);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Analysis failed. Please try again.');
      setIsAnalyzing(false);
    }
  };

  const handleClear = () => {
    setInputText('');
    setResult(null);
  };

  const handleSampleSelect = (sample) => {
    setInputText(sample);
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Real-Time Text Analyzer</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">Enter user reviews, feedback, or custom text to extract sentiment indicators.</p>
        </div>
      </div>

      {/* Input Form Block */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
        <form onSubmit={handleAnalyze} className="space-y-4">
          <div className="relative">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Paste or type text to analyze (e.g. customer feedback, tweet, survey answer)..."
              className="w-full h-40 p-4 border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950 text-slate-800 dark:text-slate-200 rounded-xl focus:border-brand-indigo focus:outline-none text-sm placeholder-slate-400 dark:placeholder-slate-600 resize-none leading-relaxed transition-colors"
              maxLength={2000}
            />
            {inputText && (
              <button
                type="button"
                onClick={handleClear}
                className="absolute top-3 right-3 p-1.5 rounded-lg text-slate-400 hover:bg-slate-200/50 dark:hover:bg-slate-800 transition-colors"
                title="Clear input"
              >
                <MdClear size={18} />
              </button>
            )}
          </div>

          {/* Form Actions */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
            {/* Quick Sample Links */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-semibold text-slate-400 flex items-center gap-1 uppercase tracking-wider">
                <MdAutoFixHigh size={14} /> Quick Examples:
              </span>
              {sampleTexts.map((sample, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSampleSelect(sample)}
                  className="text-xs px-2.5 py-1 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 rounded-full hover:bg-brand-indigo/10 hover:text-brand-indigo dark:hover:bg-brand-indigo/20 dark:hover:text-brand-indigoLight transition-all font-medium border border-transparent hover:border-brand-indigo/20"
                >
                  Example {idx + 1}
                </button>
              ))}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isAnalyzing || !inputText.trim()}
              className="w-full sm:w-auto px-6 py-3 bg-brand-indigo text-white rounded-xl font-semibold hover:bg-brand-indigoDark flex items-center justify-center gap-2 shadow-lg shadow-indigo-500/15 transition-all active:scale-98 disabled:opacity-50"
            >
              {isAnalyzing ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  Analyze Sentiment
                  <MdSend size={16} />
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Animated Results Card reveal */}
      <AnimatePresence mode="wait">
        {result && (
          <motion.div
            key="result-key"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.4 }}
          >
            <SentimentCard result={result} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Analyzer;
