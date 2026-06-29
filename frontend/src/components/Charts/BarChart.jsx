import React from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const BarChart = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-sm text-slate-400">
        No daily data available.
      </div>
    );
  }

  const isDark = document.body.classList.contains('dark');
  
  // Format labels (dates to nice strings like "June 17")
  const labels = data.map(item => {
    try {
      const parts = item.date.split('-');
      const date = new Date(parts[0], parts[1] - 1, parts[2]);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } catch {
      return item.date;
    }
  });
  
  const counts = data.map(item => item.count);

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Predictions',
        data: counts,
        backgroundColor: '#6366F1', // Indigo 500
        borderRadius: 8,
        hoverBackgroundColor: '#4F46E5', // Indigo 600
        borderSkipped: false,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false, // Hidden for cleaner SaaS look
      },
      tooltip: {
        backgroundColor: isDark ? '#1E293B' : '#0F172A',
        titleFont: { family: 'Inter', size: 12, weight: 'bold' },
        bodyFont: { family: 'Inter', size: 12 },
        padding: 10,
        cornerRadius: 8,
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: isDark ? '#94A3B8' : '#64748B',
          font: { family: 'Inter', size: 10, weight: '500' },
        },
        border: {
          display: false,
        }
      },
      y: {
        grid: {
          color: isDark ? 'rgba(148, 163, 184, 0.08)' : 'rgba(100, 116, 139, 0.08)',
        },
        ticks: {
          color: isDark ? '#94A3B8' : '#64748B',
          font: { family: 'Inter', size: 10 },
          precision: 0, // No decimals for counts
        },
        border: {
          display: false,
        }
      },
    },
  };

  return (
    <div className="relative w-full h-64">
      <Bar data={chartData} options={options} />
    </div>
  );
};

export default BarChart;
