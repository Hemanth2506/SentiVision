import React, { useState, useEffect } from 'react';
import { statsAPI } from '../api';
import { toast } from 'react-hot-toast';
import { 
  MdSearch, 
  MdFilterList, 
  MdNavigateBefore, 
  MdNavigateNext,
  MdLayersClear,
  MdHistory,
  MdRefresh
} from 'react-icons/md';

const History = () => {
  const [predictions, setPredictions] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  
  // Query parameters
  const [search, setSearch] = useState('');
  const [sentimentFilter, setSentimentFilter] = useState('');
  const [page, setPage] = useState(1);
  const limit = 10;
  
  const [isLoading, setIsLoading] = useState(true);

  // Debouncing search updates can be nice, but simple button/change triggers also work well.
  // We will run the request on search/filter/page change.
  const fetchHistory = async () => {
    setIsLoading(true);
    try {
      const data = await statsAPI.getHistory(page, limit, search, sentimentFilter);
      setPredictions(data.results);
      setTotalCount(data.total);
    } catch (err) {
      toast.error('Failed to load prediction history.');
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
      setPredictions([]);
      setTotalCount(0);
      setPage(1);
      await fetchHistory();
    } catch (err) {
      toast.error(err || "Failed to reset history data.");
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page, sentimentFilter]); // Trigger on page or filter change

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1); // Reset to page 1
    fetchHistory();
  };

  const handleResetFilters = () => {
    setSearch('');
    setSentimentFilter('');
    setPage(1);
    // Directly invoke retrieve
    statsAPI.getHistory(1, limit, '', '')
      .then(data => {
        setPredictions(data.results);
        setTotalCount(data.total);
        toast.success('Filters cleared.');
      });
  };

  const totalPages = Math.ceil(totalCount / limit) || 1;

  // Badge styler helper
  const getBadgeStyle = (sent) => {
    switch (sent) {
      case 'Positive': return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20';
      case 'Negative': return 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20';
      default: return 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20';
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Prediction History</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">View and audit all past sentiment classifications performed by your account.</p>
        </div>
        <button
          onClick={handleResetClick}
          className="opacity-20 hover:opacity-60 text-xs text-slate-400 border border-slate-500 rounded px-2 py-1.5 flex items-center gap-1.5 transition-opacity duration-300 mt-1"
        >
          <MdRefresh size={14} />
          Reset Data
        </button>
      </div>

      {/* Filters Toolbar */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-sm flex flex-col md:flex-row gap-4 items-center justify-between">
        
        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-80">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search prediction text..."
            className="w-full pl-9 pr-4 py-2 border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950 text-slate-800 dark:text-slate-200 rounded-xl focus:border-brand-indigo focus:outline-none text-xs leading-none transition-colors"
          />
          <button type="submit" className="absolute left-3 top-2.5 text-slate-400 hover:text-slate-600">
            <MdSearch size={16} />
          </button>
        </form>

        {/* Sentiment Dropdown Filter & Clear Controls */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto justify-end">
          
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-400 flex items-center gap-1 uppercase tracking-wider">
              <MdFilterList size={14} /> Filter:
            </span>
            <select
              value={sentimentFilter}
              onChange={(e) => {
                setSentimentFilter(e.target.value);
                setPage(1);
              }}
              className="px-3 py-2 border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 text-slate-700 dark:text-slate-300 rounded-xl focus:outline-none text-xs font-medium"
            >
              <option value="">All Sentiments</option>
              <option value="Positive">Positive</option>
              <option value="Neutral">Neutral</option>
              <option value="Negative">Negative</option>
            </select>
          </div>

          {(search || sentimentFilter) && (
            <button
              onClick={handleResetFilters}
              className="px-3 py-2 border border-rose-200/50 hover:bg-rose-500/10 text-rose-500 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-colors"
              title="Clear all filters"
            >
              <MdLayersClear size={14} /> Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Main Table Card */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center py-24">
            <div className="w-8 h-8 border-3 border-brand-indigo border-t-transparent rounded-full animate-spin" />
          </div>
        ) : predictions.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center px-4">
            <div className="w-16 h-16 rounded-2xl bg-indigo-50 dark:bg-slate-800 text-indigo-500 dark:text-brand-indigoLight flex items-center justify-center mb-4 border border-indigo-100/50 dark:border-slate-700/50 shadow-inner shadow-indigo-500/5">
              <MdHistory size={32} />
            </div>
            <h3 className="text-base font-bold text-slate-800 dark:text-slate-200">
              {search || sentimentFilter ? 'No matching predictions found' : 'No history recorded yet'}
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mt-2 leading-relaxed">
              {search || sentimentFilter 
                ? 'Try tweaking your search term or clearing filters to see past classifications.' 
                : 'You haven\'t run any sentiment predictions on this account yet. Head to the Text Analyzer or Bulk Analyzer to run your first check!'}
            </p>
            {(search || sentimentFilter) && (
              <button
                onClick={handleResetFilters}
                className="mt-4 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-slate-200 rounded-xl text-xs font-bold transition-all shadow-sm"
              >
                Clear Search & Filters
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50/70 border-b border-slate-100 dark:bg-slate-800/20 dark:border-slate-800">
                  <th className="p-4 font-bold text-slate-400 uppercase tracking-wider w-1/2">Input Text</th>
                  <th className="p-4 font-bold text-slate-400 uppercase tracking-wider text-center">Sentiment</th>
                  <th className="p-4 font-bold text-slate-400 uppercase tracking-wider text-center">Confidence</th>
                  <th className="p-4 font-bold text-slate-400 uppercase tracking-wider">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {predictions.map((row) => (
                  <tr key={row.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/20 transition-colors">
                    <td className="p-4 font-medium text-slate-800 dark:text-slate-200 max-w-sm truncate" title={row.input_text}>
                      {row.input_text}
                    </td>
                    <td className="p-4 text-center">
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${getBadgeStyle(row.sentiment)}`}>
                        {row.sentiment}
                      </span>
                    </td>
                    <td className="p-4 text-center font-bold text-slate-700 dark:text-slate-300">
                      {row.confidence}%
                    </td>
                    <td className="p-4 text-slate-500 dark:text-slate-400 font-medium">
                      {new Date(row.created_at).toLocaleString([], {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Controls Footer */}
        {totalPages > 1 && (
          <div className="p-4 border-t border-slate-100 dark:border-slate-800/60 flex items-center justify-between gap-4">
            <span className="text-xs text-slate-500">
              Showing Page <span className="font-semibold text-slate-800 dark:text-slate-200">{page}</span> of{' '}
              <span className="font-semibold text-slate-800 dark:text-slate-200">{totalPages}</span> ({totalCount} total)
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-1.5 border border-slate-200 dark:border-slate-800 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-40 transition-colors"
              >
                <MdNavigateBefore size={18} />
              </button>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="p-1.5 border border-slate-200 dark:border-slate-800 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-40 transition-colors"
              >
                <MdNavigateNext size={18} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default History;
