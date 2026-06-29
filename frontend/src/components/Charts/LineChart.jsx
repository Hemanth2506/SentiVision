import React from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler } from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler);

const LineChart = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-sm text-slate-400">
        No trend data available.
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

  const scores = data.map(item => item.sentiment_score);

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Positivity Index (%)',
        data: scores,
        borderColor: '#6366F1', // Indigo 500
        backgroundColor: (context) => {
          const chart = context.chart;
          const { ctx, chartArea } = chart;
          if (!chartArea) return null;
          
          const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
          gradient.addColorStop(0, 'rgba(99, 102, 241, 0.25)'); // Fade Indigo
          gradient.addColorStop(1, 'rgba(99, 102, 241, 0.00)');
          return gradient;
        },
        fill: true,
        tension: 0.4, // Smooth curve
        pointRadius: 4,
        pointBackgroundColor: '#6366F1',
        pointBorderColor: isDark ? '#0F172A' : '#FFFFFF',
        pointBorderWidth: 2,
        pointHoverRadius: 6,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: isDark ? '#1E293B' : '#0F172A',
        titleFont: { family: 'Inter', size: 12, weight: 'bold' },
        bodyFont: { family: 'Inter', size: 12 },
        padding: 10,
        cornerRadius: 8,
        callbacks: {
          label: function (context) {
            return `Positivity Index: ${context.parsed.y}%`;
          }
        }
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
          callback: function (value) {
            return value + '%';
          },
        },
        min: 0,
        max: 100,
        border: {
          display: false,
        }
      },
    },
  };

  return (
    <div className="relative w-full h-64">
      <Line data={chartData} options={options} />
    </div>
  );
};

export default LineChart;
