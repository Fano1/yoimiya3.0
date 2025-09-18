// ChatInterface.jsx
import React, { useState, useEffect } from "react";
import { socket } from "./socket"; // <-- shared socket instance

export default function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  // Listen for replies and facial movements from backend
  useEffect(() => {
    socket.on("chat_reply", (data) => {
      setMessages((prev) => [...prev, { type: "reply", text: data.text }]);
      // Here you can also handle face/emotion controls if sent by backend
      // e.g., socket.emit("update_controls", data.controls)
    });

    return () => {
      socket.off("chat_reply");
    };
  }, []);

  const sendMessage = () => {
    if (!input.trim()) return;
    setMessages((prev) => [...prev, { type: "user", text: input }]);
    socket.emit("chat_message", { text: input });
    setInput("");
  };

  return (
    <div style={{ width: "300px", padding: "10px", background: "#222", color: "#fff" }}>
      <h3>Chat</h3>
      <div style={{ maxHeight: "400px", overflowY: "auto", marginBottom: "6px" }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{ textAlign: msg.type === "user" ? "right" : "left", margin: "2px 0" }}>
            <span style={{ background: msg.type === "user" ? "#555" : "#444", padding: "4px 8px", borderRadius: "4px" }}>
              {msg.text}
            </span>
          </div>
        ))}
      </div>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type a message..."
        style={{ width: "100%", marginBottom: "4px", padding: "4px" }}
      />
      <button onClick={sendMessage} style={{ width: "100%", padding: "6px", background: "#444", border: "none", color: "#fff" }}>
        Send
      </button>
    </div>
  );
}
