import React, { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
} from "recharts";
import "./Trends.css";

const Trends = () => {
  const [trends, setTrends] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchTrends = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await fetch("http://127.0.0.1:8000/history/trends", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (response.ok) {
          const data = await response.json();
          setTrends(data);
        } else {
          setError("Failed to load trends.");
        }
      } catch (err) {
        setError("Network error.");
      } finally {
        setLoading(false);
      }
    };
    fetchTrends();
  }, []);

  if (loading) return <div className="trends-container">Loading...</div>;
  if (error) return <div className="trends-container">{error}</div>;

  if (!trends || trends.total_analyses === 0) {
    return (
      <div className="trends-container">
        <h2>Skin Trends & Analytics</h2>
        <div className="empty-state">
          <span className="icon">📈</span>
          <h3>Not enough data</h3>
          <p>Complete more skin analyses over time to unlock personalized trends and see how your skin is changing.</p>
        </div>
      </div>
    );
  }

  // Format data for Recharts
  const distributionData = Object.keys(trends.distribution).map((key) => ({
    name: key,
    count: trends.distribution[key],
  }));

  const timelineData = trends.timeline.map((t, index) => ({
    name: `Scan ${index + 1}`,
    confidence: t.confidence,
    condition: t.condition,
    date: new Date(t.date).toLocaleDateString(),
  }));

  return (
    <div className="trends-container fade-in">
      <h2>Skin Trends & Analytics</h2>
      <p className="subtitle">Track your longitudinal skin intelligence.</p>

      <div className="stats-grid">
        <div className="stat-card">
          <h4>Total Scans</h4>
          <span className="stat-value">{trends.total_analyses}</span>
        </div>
        <div className="stat-card">
          <h4>Most Frequent Concern</h4>
          <span className="stat-value">{trends.most_frequent_concern}</span>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Concern Distribution</h3>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={distributionData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <h3>Confidence Over Time</h3>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={timelineData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip labelFormatter={(label, payload) => payload[0]?.payload.date} />
                <Line
                  type="monotone"
                  dataKey="confidence"
                  stroke="#10B981"
                  strokeWidth={3}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Trends;
