import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  MdPsychology, 
  MdSpeed, 
  MdSecurity, 
  MdQueryStats, 
  MdArrowForward 
} from 'react-icons/md';

const Landing = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        delayChildren: 0.1,
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: 'easeOut' } }
  };

  const features = [
    {
      icon: MdPsychology,
      title: 'Advanced AI Pipeline',
      desc: 'Powered by 4 state-of-the-art machine learning models with automatic ensemble optimization.'
    },
    {
      icon: MdSpeed,
      title: 'Real-time Analysis',
      desc: 'Parse thousands of words per second and get instant visual confidence scoring.'
    },
    {
      icon: MdQueryStats,
      title: 'Rich Interactive Analytics',
      desc: 'Visualize sentiment distribution, positivity trends, and user activity over time.'
    },
    {
      icon: MdSecurity,
      title: 'Secure JWT Auth',
      desc: 'Industry-standard session management using secure, encrypted httpOnly cookie tokens.'
    }
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-white font-sans overflow-hidden">
      {/* Background decoration elements */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-10 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Navigation Top Bar */}
      <header className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between relative z-10">
        <Link to="/" className="flex items-center gap-2">
          <span className="w-9 h-9 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-white font-extrabold shadow-lg shadow-indigo-500/20">S</span>
          <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white to-slate-200 bg-clip-text text-transparent">
            SentiVision AI
          </span>
        </Link>
        <div className="flex items-center gap-4">
          <Link to="/login" className="text-sm font-semibold hover:text-indigo-400 transition-colors">
            Sign In
          </Link>
          <Link 
            to="/signup" 
            className="px-4 py-2 text-sm font-semibold bg-white text-slate-950 rounded-xl hover:bg-slate-100 active:scale-95 transition-all shadow-md shadow-white/5"
          >
            Get Started
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <motion.section 
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="max-w-5xl mx-auto px-6 pt-20 pb-28 text-center relative z-10"
      >
        <motion.div variants={itemVariants} className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs font-semibold text-indigo-400 mb-6">
          <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
          Production-grade ML Sentiment SaaS Platform
        </motion.div>

        <motion.h1 
          variants={itemVariants} 
          className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-[1.1] mb-6"
        >
          Understand Every Word. <br className="hidden sm:inline" />
          <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            Instantly.
          </span>
        </motion.h1>

        <motion.p 
          variants={itemVariants}
          className="text-lg text-slate-400 max-w-2xl mx-auto mb-10 font-medium"
        >
          Transform customer reviews, feedback tweets, and transcripts into actionable intelligence. Leverage advanced natural language processing to uncover emotional impact in milliseconds.
        </motion.p>

        <motion.div variants={itemVariants} className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link 
            to="/signup" 
            className="w-full sm:w-auto px-8 py-4 bg-gradient-to-tr from-indigo-600 to-purple-600 rounded-xl font-bold hover:from-indigo-500 hover:to-purple-500 transition-all flex items-center justify-center gap-2 group shadow-lg shadow-indigo-500/20 active:scale-98"
          >
            Create Free Account
            <MdArrowForward size={18} className="group-hover:translate-x-1 transition-transform" />
          </Link>
          <Link 
            to="/login" 
            className="w-full sm:w-auto px-8 py-4 bg-slate-900 border border-slate-800 rounded-xl font-bold hover:bg-slate-800/80 transition-colors"
          >
            Live Demo
          </Link>
        </motion.div>

        {/* Floating SaaS Mockup Preview */}
        <motion.div
          variants={itemVariants}
          animate={{
            y: [0, -10, 0],
          }}
          transition={{
            duration: 6,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="mt-16 relative mx-auto max-w-4xl rounded-2xl border border-slate-800 bg-slate-950/70 p-4 shadow-2xl shadow-indigo-500/10 backdrop-blur-xl"
        >
          {/* Mock Window Controls */}
          <div className="flex items-center gap-1.5 border-b border-slate-900 pb-3 mb-4">
            <div className="w-3.5 h-3.5 rounded-full bg-rose-500/60" />
            <div className="w-3.5 h-3.5 rounded-full bg-amber-500/60" />
            <div className="w-3.5 h-3.5 rounded-full bg-emerald-500/60" />
            <span className="text-[10px] text-slate-500 font-mono ml-4">app.sentivision.ai/analyzer</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
            {/* Input area */}
            <div className="md:col-span-2 p-4 rounded-xl bg-slate-900/50 border border-slate-800/60 flex flex-col justify-between h-44">
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Review Input</span>
              <p className="text-sm font-medium text-slate-300 leading-relaxed mt-2">
                "The brand new display supports USB-C charging and features an amazing 120Hz refresh rate. I am extremely happy with this purchase!"
              </p>
              <div className="flex items-center justify-between text-[10px] text-indigo-400 font-bold tracking-wider mt-4">
                <span>MODEL PIPELINE READY</span>
                <span className="px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20">SVM ACTIVE</span>
              </div>
            </div>

            {/* Results card */}
            <div className="p-4 rounded-xl bg-gradient-to-br from-indigo-950/40 to-slate-900 border border-brand-indigo/20 shadow-lg shadow-indigo-500/5 flex flex-col justify-between h-44">
              <div>
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Detected Sentiment</span>
                <span className="text-xl font-bold text-emerald-400 mt-2 block flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
                  Positive
                </span>
                <span className="text-xs text-slate-400 mt-1 block">98.5% Confidence</span>
              </div>

              {/* Stacked confidence mockup */}
              <div className="space-y-1.5 mt-4">
                <div className="flex justify-between text-[9px] font-bold text-slate-400">
                  <span>POS: 98%</span>
                  <span>NEU: 1%</span>
                  <span>NEG: 1%</span>
                </div>
                <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden flex">
                  <div className="h-full bg-emerald-500" style={{ width: '98%' }} />
                  <div className="h-full bg-amber-500" style={{ width: '1%' }} />
                  <div className="h-full bg-rose-500" style={{ width: '1%' }} />
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.section>

      {/* Features Grid Section */}
      <section className="max-w-6xl mx-auto px-6 pb-32 relative z-10">
        <div className="text-center mb-16">
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight mb-4">Engineered for Actionable Insights</h2>
          <p className="text-sm text-slate-400 max-w-md mx-auto">Get full visibility on user feedback with our developer-first sentiment platform.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feat, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1, duration: 0.5 }}
              whileHover={{ y: -5 }}
              className="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-700/60 transition-all shadow-lg flex flex-col"
            >
              <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-6">
                <feat.icon size={24} />
              </div>
              <h3 className="text-lg font-bold mb-2">{feat.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed mt-auto">{feat.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-10 text-center text-xs text-slate-500 relative z-10 bg-slate-950">
        <p>&copy; {new Date().getFullYear()} SentiVision AI. All rights reserved.</p>
        <p className="mt-2 text-slate-600">Built using React, FastAPI, SQLite, and Scikit-Learn.</p>
      </footer>
    </div>
  );
};

export default Landing;
