import React, { useState, useEffect } from "react";
import { transactionsAPI } from "../services/api";
import "../styles/Transactions.css";

function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      console.log('📊 Fetching transactions...');
      const response = await transactionsAPI.list(0, 100);
      console.log('✅ Transactions loaded:', response.data);
      setTransactions(response.data);
      setError(null);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || "Failed to load transactions";
      console.error('❌ Error loading transactions:', errorMsg);
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTransaction = async (transactionId) => {
    if (!window.confirm('Are you sure you want to delete this transaction?')) {
      return;
    }
    try {
      console.log('🗑️ Deleting transaction:', transactionId);
      await transactionsAPI.delete(transactionId);
      console.log('✅ Transaction deleted successfully');
      setError(null);
      fetchTransactions();
      alert('✅ Transaction deleted successfully!');
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to delete transaction';
      console.error('❌ Error deleting transaction:', errorMsg);
      setError(errorMsg);
      alert('❌ Error: ' + errorMsg);
    }
  };

  if (loading) return <div className="loading">Loading transactions...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="transactions-page">
      <h1>Transactions</h1>

      <div className="table-container">
        <table className="transactions-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Product</th>
              <th>Quantity</th>
              <th>Price</th>
              <th>Total</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {transactions.length === 0 ? (
              <tr>
                <td colSpan="7" className="text-center">
                  No transactions found
                </td>
              </tr>
            ) : (
              transactions.map((t) => (
                <tr key={t.id}>
                  <td>{t.id}</td>
                  <td>{t.product?.name || "Unknown"}</td>
                  <td>{t.quantity}</td>
                  <td>${t.unit_price}</td>
                  <td>${t.total_price}</td>
                  <td>{new Date(t.transaction_date).toLocaleDateString()}</td>
                  <td>
                    <button
                      onClick={() => handleDeleteTransaction(t.id)}
                      className="btn-delete"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Transactions;
