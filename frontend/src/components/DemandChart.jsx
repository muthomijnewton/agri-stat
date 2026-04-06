import React, { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { transactionsAPI } from "../services/api";

function DemandChart() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTransactionData();
  }, []);

  const fetchTransactionData = async () => {
    try {
      const response = await transactionsAPI.list(0, 100);
      const grouped = {};

      response.data.forEach((t) => {
        const date = t.transaction_date;
        if (!grouped[date]) {
          grouped[date] = { date, quantity: 0 };
        }
        grouped[date].quantity += t.quantity;
      });

      const sorted = Object.values(grouped)
        .sort((a, b) => new Date(a.date) - new Date(b.date))
        .slice(-30);

      setData(sorted);
    } catch (err) {
      console.error("Error fetching transaction data:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="chart-container loading">Loading...</div>;
  if (data.length === 0)
    return <div className="chart-container">No data available</div>;

  return (
    <div className="chart-container">
      <h2>Demand Trends</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="quantity" stroke="#8884d8" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default DemandChart;
