import React, { useState, useEffect } from "react";

function Chat({ postId, currentUserId }) {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");

  // Fetch chats whenever postId changes
  useEffect(() => {
    const fetchChats = async () => {
      if (!postId) return;
      try {
        const res = await fetch(`http://localhost:5000/api/post/${postId}/chats`);
        const data = await res.json();
        setMessages(data);
      } catch (err) {
        console.error("Failed to fetch chats:", err);
      }
    };
    fetchChats();
  }, [postId]);

  const sendMessage = async () => {
    if (!newMessage.trim()) return; // ignore empty messages
    try {
      const res = await fetch(`http://localhost:5000/api/post/${postId}/chats`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sender_id: currentUserId,
          message: newMessage.trim()
        }),
      });
      const result = await res.json();
      if (res.ok) {
        setNewMessage("");
        // Refresh messages
        const chatRes = await fetch(`http://localhost:5000/api/post/${postId}/chats`);
        const chatData = await chatRes.json();
        setMessages(chatData);
      } else {
        console.error("Failed to send message:", result.error);
      }
    } catch (err) {
      console.error("Error sending message:", err);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.length === 0 && <p>No messages yet.</p>}
        {messages.map((msg) => (
          <p key={msg.id}><strong>{msg.sender_name}:</strong> {msg.message}</p>
        ))}
      </div>
      <div className="chat-input">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Type a message..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default Chat;
