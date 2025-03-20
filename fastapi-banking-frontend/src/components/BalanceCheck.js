import React, { useState } from "react";
import axios from "axios";

const BalanceCheck = () => {
  const [accountId, setAccountId] = useState(""); // State for account ID
  const [balance, setBalance] = useState(null); // State for balance
  const [message, setMessage] = useState(""); // State for error messages

  const fetchBalance = async () => {
    if (!accountId.trim()) {
      setMessage("Please enter an account ID.");
      return;
    }

    try {
      const cleanAccountId = accountId.trim();
      const response = await axios.get(`http://127.0.0.1:8000/accounts/${cleanAccountId}/balance`);
      setBalance(response.data.balance);
      setMessage("");
    } catch (error) {
      setMessage(error.response?.data?.detail || "Account not found");
      setBalance(null);
    }
  };

  return (
    <div className="p-4 border rounded shadow bg-white">
      <h2 className="text-xl font-semibold mb-2">Check Balance</h2>
      <input
        type="text"
        placeholder="Enter Account ID"
        value={accountId}
        onChange={(e) => setAccountId(e.target.value)}
        className="border p-2 rounded w-full mb-2"
      />
      <button onClick={fetchBalance} className="bg-blue-500 text-white px-4 py-2 rounded">
        Check Balance
      </button>
      {balance !== null && <p className="mt-2">Balance: ${balance.toFixed(2)}</p>}
      {message && <p className="text-red-500">{message}</p>}
    </div>
  );
};

export default BalanceCheck;
