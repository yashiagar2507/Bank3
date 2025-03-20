import React, { useState } from "react";
import axios from "axios";

const TransactionForm = () => {
  const [accountId, setAccountId] = useState("");
  const [amount, setAmount] = useState("");
  const [message, setMessage] = useState("");

  const handleTransaction = async (type) => {
    try {
      const response = await axios.post(`http://localhost:8000/transactions/${type}`, {
        account_id: accountId,
        amount: parseFloat(amount),
      });
      setMessage(response.data.message);
    } catch (error) {
      setMessage(error.response?.data?.detail || "Transaction failed");
    }
  };

  return (
    <div className="p-4 border rounded shadow bg-white mt-4">
      <h2 className="text-xl font-semibold mb-2">Make a Transaction</h2>
      <input
        type="text"
        placeholder="Enter Account ID"
        value={accountId}
        onChange={(e) => setAccountId(e.target.value)}
        className="border p-2 rounded w-full mb-2"
      />
      <input
        type="number"
        placeholder="Enter Amount"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        className="border p-2 rounded w-full mb-2"
      />
      <button onClick={() => handleTransaction("credit")} className="bg-green-500 text-white px-4 py-2 rounded mr-2">
        Credit
      </button>
      <button onClick={() => handleTransaction("debit")} className="bg-red-500 text-white px-4 py-2 rounded">
        Debit
      </button>
      {message && <p className="mt-2">{message}</p>}
    </div>
  );
};

export default TransactionForm;
