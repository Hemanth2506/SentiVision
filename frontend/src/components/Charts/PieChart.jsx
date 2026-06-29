import React from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Pie } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend);

const PieChart = ({ data }) => {
  if (!data) return null;

  const { positive = 0, negative = 0, neutral = 0 } = data;
  const isDark = document.body.classList.contains('dark');

  // Chart configuration
  const chartData = {
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [
      {
        data: [positive, neutral, negative],
        backgroundColor: [
          '#10B981', // Emerald 500
          '#F59E0B', // Amber 500
          '#EF4444', // Rose 500
        ],
        borderColor: isDark ? '#0F172A' : '#FFFFFF',
        borderWidth: 2,
        hoverOffset: 4,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: isDark ? '#94A3B8' : '#475569', // Slate 400 vs Slate 600
          font: {
            family: 'Inter',
            size: 12,
            weight: '500',
          },
          padding: 15,
          usePointStyle: true,
        },
      },
      tooltip: {
        backgroundColor: isDark ? '#1E293B' : '#0F172A',
        titleFont: { family: 'Inter', size: 12, weight: 'bold' },
        bodyFont: { family: 'Inter', size: 12 },
        padding: 10,
        cornerRadius: 8,
        displayColors: true,
      },
    },
  };

  return (
    <div className="relative w-full h-64">
      <Pie data={chartData} options={options} />
    </div>
  );
};

export default PieChart;
