import React, { useState } from "react";
import "./Assistant.css";

const Assistant = () => {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([
    {
      sender: "ai",
      text: "Hello! I am Lumine AI, your personal skin health assistant. How can I help you today?"
    }
  ]);
  const [loading, setLoading] = useState(false);

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    const userMessage = { sender: "user", text: question };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setLoading(true);

    try {
      const token = localStorage.getItem("token");
      const response = await fetch("http://127.0.0.1:8000/assistant/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ question: userMessage.text }),
      });
      const data = await response.json();
      
      if (response.ok) {
        setMessages((prev) => [...prev, { sender: "ai", text: data.answer }]);
      } else {
        setMessages((prev) => [...prev, { sender: "ai", text: "I'm sorry, I encountered an error." }]);
      }
    } catch (err) {
      setMessages((prev) => [...prev, { sender: "ai", text: "I'm having trouble connecting to the server." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="assistant-container fade-in">
      <h2>Lumine AI Assistant</h2>
      <p className="subtitle">Ask questions about your skin history and trends.</p>

      <div className="chat-window">
        <div className="chat-history">
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-message ${msg.sender}`}>
              <div className="chat-bubble">
                {msg.text}
              </div>
            </div>
          ))}
          {loading && (
            <div className="chat-message ai">
              <div className="chat-bubble loading">
                Thinking...
              </div>
            </div>
          )}
        </div>
        
        <form onSubmit={handleAsk} className="chat-input-area">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g., What is my most common concern?"
            disabled={loading}
          />
          <button type="submit" className="btn-primary" disabled={loading || !question.trim()}>
            Ask
          </button>
        </form>
      </div>
      <p className="disclaimer mt-4">
        Lumine AI cannot diagnose medical conditions. Please consult a dermatologist for professional medical advice.
      </p>
    </div>
  );
};

export default Assistant;
