import React, { useState, useRef, useEffect } from 'react';
import './ChatWindow.css';
import ReactMarkdown from 'react-markdown';

const ChatWindow = ({ }) => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
  const fetchChatHistory = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/chat/history/");
      const data = await res.json();
      if (res.ok) {
        // Map backend keys to frontend format
        const formatted = data.map(msg => ({
          type: msg.message_type,
          text: msg.message,
        }));
        setMessages(formatted);
      }
    } catch (error) {
      console.error("Failed to fetch chat history:", error);
    }
  };

  fetchChatHistory();
}, []);


  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input.trim();

    // Add user message to chat
    setMessages((prev) => [...prev, { type: 'user', text: userMessage }]);
    setInput('');

    try {
      const res = await fetch('http://localhost:8000/api/chat/ask/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage }),
      });

      const data = await res.json();

      if (res.ok && data.answer) {
        setMessages((prev) => [...prev, { type: 'ai', text: data.answer }]);
      } else {
        setMessages((prev) => [
          ...prev,
          { type: 'ai', text: 'Sorry, something went wrong.' },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { type: 'ai', text: 'Network error. Please try again.' },
      ]);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const markdownComponents = {
  p: ({ children }) => <span>{children}</span>,  // Render paragraphs inline as spans
};

  return (
    <div className="chat-window">
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`chat-message ${msg.type === 'user' ? 'user-message' : 'ai-message'}`}
          >
            {msg.type === 'ai' ? <ReactMarkdown components={markdownComponents}>{msg.text}</ReactMarkdown> : msg.text}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <input
          className="chat-input"
          type="text"
          placeholder="Ask a question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <button className="send-button" onClick={handleSend}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatWindow;
