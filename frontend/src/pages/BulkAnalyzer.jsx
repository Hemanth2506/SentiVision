import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { analyzerAPI } from '../api';
import { 
  MdCloudUpload, 
  MdFileDownload, 
  MdInsertDriveFile, 
  MdCancel,
  MdSentimentSatisfied,
  MdSentimentDissatisfied,
  MdSentimentNeutral 
} from 'react-icons/md';

const BulkAnalyzer = () => {
  const [file, setFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState([]);
  const [dragActive, setDragActive] = useState(false);
  
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile) => {
    const name = selectedFile.name.toLowerCase();
    if (name.endsWith('.csv') || name.endsWith('.txt')) {
      setFile(selectedFile);
      setResults([]); // Reset previous results
    } else {
      toast.error('Only CSV and TXT files are supported.');
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  const clearFile = () => {
    setFile(null);
    setResults([]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setIsProcessing(true);
    try {
      const data = await analyzerAPI.analyzeBatch(file);
      // Premium visual timeout delay
      setTimeout(() => {
        setResults(data);
        setIsProcessing(false);
        toast.success(`Successfully analyzed ${data.length} records!`);
      }, 800);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to process bulk analysis.');
      setIsProcessing(false);
    }
  };

  // Client-side export helper
  const exportToCSV = () => {
    if (results.length === 0) return;

    const headers = ['Text', 'Sentiment', 'Confidence (%)', 'Pos Prob (%)', 'Neu Prob (%)', 'Neg Prob (%)'];
    const rows = results.map(r => [
      // Escape commas and quotes for CSV format safety
      `"${r.input_text.replace(/"/g, '""')}"`,
      r.sentiment,
      r.confidence,
      r.pos_prob,
      r.neu_prob,
      r.neg_prob
    ]);

    const csvContent = "data:text/csv;charset=utf-8," 
      + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
      
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `sentivision_bulk_export_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success('CSV Export downloaded!');
  };

  // Helper mapping sentiment style
  const getBadgeStyle = (sent) => {
    switch (sent) {
      case 'Positive': return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20';
      case 'Negative': return 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20';
      default: return 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20';
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Bulk Sentiment Analyzer</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">Upload bulk CSV or TXT files to evaluate sentiment. First column of CSV will be read if text-related headers are missing.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        
        {/* Left Side: Upload zone */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6">
          <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest leading-none">Upload Source File</h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div
              className={`
                relative border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-300 overflow-hidden
                ${dragActive 
                  ? 'border-brand-indigo bg-brand-indigo/10 dark:bg-brand-indigo/20 scale-[1.02] shadow-lg shadow-brand-indigo/10' 
                  : 'border-slate-200 dark:border-slate-800 bg-slate-50/20 dark:bg-slate-900/30 hover:border-slate-300 dark:hover:border-slate-700 hover:bg-slate-50/50 dark:hover:bg-slate-800/10'}
                ${file ? 'border-solid border-indigo-500/30 bg-indigo-500/[0.02] dark:bg-indigo-500/[0.05]' : ''}
              `}
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              onClick={!file ? handleUploadClick : undefined}
            >
              {/* Pulsing background glow on drag over */}
              {dragActive && (
                <div className="absolute inset-0 bg-gradient-to-tr from-brand-indigo/5 to-purple-500/5 animate-pulse pointer-events-none" />
              )}

              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept=".csv,.txt"
                onChange={handleFileChange}
              />
              
              <AnimatePresence mode="wait">
                {!file ? (
                  <motion.div
                    key="prompt"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="flex flex-col items-center"
                  >
                    <motion.div 
                      animate={dragActive ? { scale: 1.15, rotate: [0, -5, 5, 0] } : { scale: 1 }}
                      transition={{ duration: 0.3 }}
                      className="w-12 h-12 rounded-xl bg-indigo-500/10 text-brand-indigo flex items-center justify-center mb-4 border border-indigo-500/20 shadow-sm shadow-indigo-500/5"
                    >
                      <MdCloudUpload size={24} className={dragActive ? "animate-bounce" : ""} />
                    </motion.div>
                    <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                      {dragActive ? "Drop to upload file!" : "Drag & drop your file here"}
                    </p>
                    <p className="text-xs text-slate-400 mt-1">or click to browse files</p>
                    <p className="text-[10px] text-slate-400 mt-4 font-mono">Supports CSV and TXT (Max 500 rows)</p>
                  </motion.div>
                ) : (
                  <motion.div
                    key="file-info"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="w-full flex items-center justify-between gap-3"
                  >
                    <div className="w-10 h-10 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-500 flex items-center justify-center flex-shrink-0 shadow-sm">
                      <MdInsertDriveFile size={22} className="text-brand-indigo" />
                    </div>
                    <div className="flex-1 text-left min-w-0">
                      <p className="text-sm font-semibold truncate text-slate-700 dark:text-slate-300">{file.name}</p>
                      <p className="text-xs text-slate-400">{(file.size / 1024).toFixed(2)} KB</p>
                    </div>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation(); // Avoid triggering open file dialog
                        clearFile();
                      }}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-rose-500 hover:bg-slate-200/50 dark:hover:text-rose-400 dark:hover:bg-slate-700/50 transition-all"
                    >
                      <MdCancel size={20} />
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <button
              type="submit"
              disabled={!file || isProcessing}
              className="w-full py-3.5 bg-brand-indigo text-white font-semibold rounded-xl hover:bg-brand-indigoDark flex items-center justify-center gap-2 shadow-lg shadow-indigo-500/15 transition-all active:scale-98 disabled:opacity-50"
            >
              {isProcessing ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Analyzing bulk rows...
                </>
              ) : (
                'Run Bulk Analysis'
              )}
            </button>
          </form>
        </div>

        {/* Right Side: Results Log */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
            <div className="flex items-center justify-between gap-4 mb-6">
              <div>
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest leading-none">Analysis Output Log</h3>
                {results.length > 0 && (
                  <p className="text-xs text-slate-400 mt-2">Parsed {results.length} text records successfully.</p>
                )}
              </div>
              
              {results.length > 0 && (
                <button
                  onClick={exportToCSV}
                  className="px-4 py-2 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
                >
                  <MdFileDownload size={16} />
                  Export CSV
                </button>
              )}
            </div>

            {results.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 text-center">
                <div className="w-14 h-14 rounded-full bg-slate-50 dark:bg-slate-800 flex items-center justify-center text-slate-400 mb-4 border border-slate-200/50 dark:border-slate-700">
                  <MdInsertDriveFile size={26} />
                </div>
                <p className="text-sm font-semibold text-slate-600 dark:text-slate-400">No output generated yet</p>
                <p className="text-xs text-slate-400 mt-1">Upload a CSV or TXT data source and click Run.</p>
              </div>
            ) : (
              <div className="overflow-x-auto border border-slate-100 dark:border-slate-800 rounded-xl">
                <table className="w-full text-left text-sm border-collapse">
                  <thead>
                    <tr className="bg-slate-50/70 border-b border-slate-100 dark:bg-slate-800/20 dark:border-slate-800">
                      <th className="p-4 font-semibold text-slate-500 dark:text-slate-400 w-2/3">Input Text</th>
                      <th className="p-4 font-semibold text-slate-500 dark:text-slate-400 text-center">Sentiment</th>
                      <th className="p-4 font-semibold text-slate-500 dark:text-slate-400 text-center">Confidence</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {results.map((row, idx) => (
                      <tr key={idx} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/20 transition-colors">
                        <td className="p-4 truncate max-w-md font-medium text-slate-700 dark:text-slate-300">
                          {row.input_text}
                        </td>
                        <td className="p-4 text-center">
                          <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${getBadgeStyle(row.sentiment)}`}>
                            {row.sentiment}
                          </span>
                        </td>
                        <td className="p-4 text-center font-bold text-slate-600 dark:text-slate-400">
                          {row.confidence}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default BulkAnalyzer;
