import React from "react";
import BalanceCheck from "./components/BalanceCheck";
import TransactionForm from "./components/TransactionForm";

function App() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-6">
      <h1 className="text-3xl font-bold mb-6">FastAPI Banking System</h1>
      <BalanceCheck />
      <TransactionForm />
    </div>
  );
}

export default App;
