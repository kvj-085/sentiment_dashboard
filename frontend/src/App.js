import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar, Pie } from 'react-chartjs-2';
import './App.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const API_URL = 'http://localhost:8000/api';

function App() {
  const [stats, setStats] = useState(null);
  const [recentSentiments, setRecentSentiments] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, recentRes, timelineRes] = await Promise.all([
        axios.get(`${API_URL}/sentiments/stats?hours=24`),
        axios.get(`${API_URL}/sentiments/recent?limit=10`),
        axios.get(`${API_URL}/sentiments/timeline?hours=24`)
      ]);

      setStats(statsRes.data);
      setRecentSentiments(recentRes.data);
      setTimeline(timelineRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const pieData = stats ? {
    labels: ['Positive', 'Negative'],
    datasets: [
      {
        data: [stats.positive_count, stats.negative_count],
        backgroundColor: ['#00ff88', '#ff0055'],
        borderColor: ['#00ffff', '#ff00aa'],
        borderWidth: 2,
      },
    ],
  } : null;

  const barData = stats ? {
    labels: ['Positive', 'Negative'],
    datasets: [
      {
        label: 'Sentiment Count',
        data: [stats.positive_count, stats.negative_count],
        backgroundColor: ['rgba(0, 255, 136, 0.7)', 'rgba(255, 0, 85, 0.7)'],
        borderColor: ['#00ff88', '#ff0055'],
        borderWidth: 2,
        borderRadius: 8,
      },
    ],
  } : null;

  // Dark neon theme for charts
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        labels: {
          color: '#e0e0e0',
          font: { size: 13, weight: 600 },
        },
      },
    },
    scales: {
      y: {
        ticks: { color: '#a0a0b0' },
        grid: { color: 'rgba(0, 255, 255, 0.05)' },
      },
      x: {
        ticks: { color: '#a0a0b0' },
        grid: { color: 'rgba(0, 255, 255, 0.05)' },
      },
    },
  };

  if (loading) {
    return (
      <div className="App">
        <div className="loading">Loading sentiment data...</div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="header">
        <h1>🎭Real-Time Sentiment Dashboard</h1>
        <p>Analyzing sentiment trends in real-time</p>
      </header>

      <div className="container">
        {/* Stats Cards */}
        <div className="stats-grid">
          <div className="stat-card">
            <h3>Total Analyzed</h3>
            <p className="stat-value">{stats?.total_count || 0}</p>
          </div>
          <div className="stat-card positive">
            <h3>Positive</h3>
            <p className="stat-value">{stats?.positive_percentage?.toFixed(1) || 0}%</p>
          </div>
          <div className="stat-card negative">
            <h3>Negative</h3>
            <p className="stat-value">{stats?.negative_percentage?.toFixed(1) || 0}%</p>
          </div>
          <div className="stat-card">
            <h3>Avg Confidence</h3>
            <p className="stat-value">{(stats?.average_score * 100)?.toFixed(1) || 0}%</p>
          </div>
        </div>

        {/* Charts */}
        <div className="charts-grid">
          <div className="chart-card">
            <h2>Sentiment Distribution</h2>
            {pieData && <Pie data={pieData} options={chartOptions} />}
          </div>
          <div className="chart-card">
            <h2>Sentiment Comparison</h2>
            {barData && <Bar data={barData} options={chartOptions} />}
          </div>
        </div>

        {/* Recent Sentiments */}
        <div className="recent-section">
          <h2>Recent Analyses</h2>
          <div className="recent-list">
            {recentSentiments.map((item, index) => (
              <div
                key={index}
                className={`recent-item ${item.sentiment.toLowerCase()}`}
              >
                <div className="recent-text">{item.text}</div>
                <div className="recent-meta">
                  <span className={`sentiment-badge ${item.sentiment.toLowerCase()}`}>
                    {item.sentiment}
                  </span>
                  <span className="confidence">{(item.score * 100).toFixed(1)}%</span>
                  <span className="source">{item.source}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
