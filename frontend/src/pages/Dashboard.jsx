import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { statsAPI } from '../api';
import { toast } from 'react-hot-toast';
import PieChart from '../components/Charts/PieChart';
import BarChart from '../components/Charts/BarChart';
import LineChart from '../components/Charts/LineChart';
import { 
  MdCompareArrows,
  MdThumbUp,
  MdThumbDown,
  MdRemove,
  MdArrowUpward,
  MdQueryStats,
  MdHistory,
  MdSentimentNeutral,
  MdRefresh
} from 'react-icons/md';

// Helper component for count-up animation using requestAnimationFrame
const AnimatedCounter = ({ value, suffix = '' }) => {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    let startTimestamp = null;
    const endValue = parseFloat(value) || 0;
    const duration = 1000; // 1 second smooth duration
    
    if (endValue === 0) {
      setDisplayValue(0);
      return;
    }

    let animationFrameId;

    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const elapsed = timestamp - startTimestamp;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function: easeOutQuad
      const easeProgress = progress * (2 - progress);
      const currentValue = easeProgress * endValue;
      
      setDisplayValue(currentValue);

      if (progress < 1) {
        animationFrameId = requestAnimationFrame(step);
      } else {
        setDisplayValue(endValue);
      }
    };

    animationFrameId = requestAnimationFrame(step);

    return () => {
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
    };
  }, [value]);

  const formatted = suffix === '%' 
    ? displayValue.toFixed(1) + '%' 
    : Math.floor(displayValue).toLocaleString();

  return <span>{formatted}</span>;
};

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchDashboardStats = async () => {
    try {
      const data = await statsAPI.getStats();
      setStats(data);
    } catch (err) {
      toast.error('Failed to retrieve dashboard analytics.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetClick = async () => {
    const confirmed = window.confirm("This will permanently delete all your analysis history. Are you sure?");
    if (!confirmed) return;

    try {
      await statsAPI.resetData();
      toast.success("Data reset successfully");
      await fetchDashboardStats();
    } catch (err) {
      toast.error(err || "Failed to reset dashboard data.");
    }
  };

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-brand-indigo border-t-transparent rounded-full animate-spin" />
          <p className="text-sm font-semibold text-slate-500">Loading Dashboard Metrics...</p>
        </div>
      </div>
    );
  }

  const { kpis, pie_chart, bar_chart, trend_chart, recent_activity } = stats || {
    kpis: { total: 0, positive_pct: 0, negative_pct: 0, neutral_pct: 0 },
    pie_chart: { positive: 0, negative: 0, neutral: 0 },
    bar_chart: [],
    trend_chart: [],
    recent_activity: []
  };

  const kpiCards = [
    {
      title: 'Total Analyzed',
      value: kpis.total,
      suffix: '',
      icon: MdQueryStats,
      color: 'text-indigo-500 bg-indigo-500/10 border-indigo-500/15',
    },
    {
      title: 'Positive Ratio',
      value: kpis.positive_pct,
      suffix: '%',
      icon: MdThumbUp,
      color: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/15',
    },
    {
      title: 'Neutral Ratio',
      value: kpis.neutral_pct,
      suffix: '%',
      icon: MdSentimentNeutral,
      color: 'text-amber-500 bg-amber-500/10 border-amber-500/15',
    },
    {
      title: 'Negative Ratio',
      value: kpis.negative_pct,
      suffix: '%',
      icon: MdThumbDown,
      color: 'text-rose-500 bg-rose-500/10 border-rose-500/15',
    },
  ];

  const getBadgeStyle = (sent) => {
    switch (sent) {
      case 'Positive': return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20';
      case 'Negative': return 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20';
      default: return 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20';
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Analytics Dashboard</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">Track and monitor NLP classification trends across your pipelines.</p>
        </div>
        <button
          onClick={handleResetClick}
          className="opacity-20 hover:opacity-60 text-xs text-slate-400 border border-slate-500 rounded px-2 py-1.5 flex items-center gap-1.5 transition-opacity duration-300 mt-1"
        >
          <MdRefresh size={14} />
          Reset Data
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpiCards.map((card, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.08 }}
            className="p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm flex items-center justify-between"
          >
            <div className="space-y-2">
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest leading-none">{card.title}</p>
              <h3 className="text-3xl font-extrabold text-slate-800 dark:text-white">
                <AnimatedCounter value={card.value} suffix={card.suffix} />
              </h3>
            </div>
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center border ${card.color}`}>
              <card.icon size={22} />
            </div>
          </motion.div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pie chart (Sentiment distribution) */}
        <div className="p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm flex flex-col justify-between">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Sentiment Distribution</h4>
          <PieChart data={pie_chart} />
        </div>

        {/* Bar Chart (Daily count) */}
        <div className="p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm lg:col-span-2 flex flex-col justify-between">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Daily Analysis volume (7 Days)</h4>
          <BarChart data={bar_chart} />
        </div>
      </div>

      {/* Line Chart & Recent Activity Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Trend Line Chart (Sentiment over time) */}
        <div className="p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm lg:col-span-2 flex flex-col justify-between">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Positivity Index Trend</h4>
          <LineChart data={trend_chart} />
        </div>

        {/* Recent Activity Feed */}
        <div className="p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm flex flex-col justify-between">
          <div>
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Recent Activity</h4>
            
            {recent_activity.length === 0 ? (
              <p className="text-xs text-slate-400 text-center py-12">No recent analyses run.</p>
            ) : (
              <div className="space-y-4 max-h-72 overflow-y-auto pr-1">
                {recent_activity.slice(0, 5).map((act, index) => (
                  <div key={index} className="flex items-center justify-between gap-3 text-xs border-b border-slate-100 dark:border-slate-800/60 pb-3 last:border-0 last:pb-0">
                    <div className="flex-1 min-w-0 pr-2">
                      <p className="font-semibold text-slate-700 dark:text-slate-300 truncate">{act.input_text}</p>
                      <p className="text-[10px] text-slate-400 mt-1">
                        {new Date(act.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold flex-shrink-0 ${getBadgeStyle(act.sentiment)}`}>
                      {act.sentiment}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

      </div>

    </div>
  );
};

export default Dashboard;
