import React, { useEffect, useState } from "react";
import CreatePost from "./createpost.js";
import "./main.css";

// Geocoding function using OpenStreetMap
async function getLatLng(city) {
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(city)}`
    );
    const data = await res.json();
    if (!data.length) return null;
    return { lat: parseFloat(data[0].lat), lng: parseFloat(data[0].lon) };
  } catch (err) {
    console.error("Geocoding error:", err);
    return null;
  }
}

function Main() {
  const [user] = useState(() => {
    const storedUser = localStorage.getItem("user");
    return storedUser ? JSON.parse(storedUser) : null;
  });

  const [search, setSearch] = useState("");
  const [budget, setBudget] = useState("");
  const [location, setLocation] = useState("");
  const [recommendations, setRecommendations] = useState([]);
  const [myPosts, setMyPosts] = useState([]);
  const [searchResults, setSearchResults] = useState([]); // only for searched posts
  const [activeChatPost, setActiveChatPost] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");

  // Fetch my posts
  useEffect(() => {
    if (!user?.id) return;
    const fetchMyPosts = async () => {
      try {
        const res = await fetch(`http://localhost:5000/api/solo-traveller/my-posts/${user.id}`);
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        const data = await res.json();
        setMyPosts(data);
      } catch (err) {
        console.error("Failed to fetch my posts:", err);
      }
    };
    fetchMyPosts();
  }, [user?.id]);

  // Recommendations
  const handleGetRecommendations = async () => {
    if (!budget || !location) return alert("Please enter both budget and location");
    try {
      const coords = await getLatLng(location);
      if (!coords) return alert("Could not find coordinates for the location");

      const response = await fetch("http://localhost:5000/api/recommendations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: user.id,
          hobbies: user.hobbies || [],
          budget: Number(budget),
          lat: coords.lat,
          lng: coords.lng
        }),
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setRecommendations(data.recommendations || []);
      setSearchResults([]); // clear search results
    } catch (err) {
      console.error("Error fetching recommendations:", err);
      alert("Failed to fetch recommendations. Check console.");
    }
  };

  // Search posts
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!search) return;
    try {
      const response = await fetch(`http://localhost:5000/api/solo-traveller/destination/${search}`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setSearchResults(data);
      setRecommendations([]); // hide regular recommendations
    } catch (err) {
      console.error("Error during search:", err);
      alert("Failed to search posts. Check console.");
    }
  };

  // Open chat for a post
  const openChat = async (postId) => {
    setActiveChatPost(postId);
    try {
      const res = await fetch(`http://localhost:5000/api/post/${postId}/chats`);
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      const data = await res.json();
      setChatMessages(data);
    } catch (err) {
      console.error("Failed to fetch chats:", err);
    }
  };

  // Send new chat message
  const sendMessage = async () => {
    if (!newMessage.trim()) return;
    try {
      const res = await fetch(`http://localhost:5000/api/post/${activeChatPost}/chats`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sender_id: user.id,
          receiver_id: 0, // 0 or dynamically assign later
          message: newMessage
        }),
      });
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      setChatMessages(prev => [...prev, { sender_name: user.name, message: newMessage }]);
      setNewMessage("");
    } catch (err) {
      console.error("Failed to send message:", err);
    }
  };

  return (
    <div className="main-container" style={{ backgroundColor: "#ae8cff", minHeight: "100vh", paddingBottom: "50px" }}>
      <h2 className="genz-heading">Welcome, {user?.name || "Traveler"}! 🌎</h2>

      {/* Budget & Location */}
      <div className="filter-container">
        <input type="number" placeholder="Enter your budget (INR)" value={budget} onChange={e => setBudget(e.target.value)} />
        <input type="text" placeholder="Enter your location/city" value={location} onChange={e => setLocation(e.target.value)} />
        <button onClick={handleGetRecommendations}>Get Recommendations</button>
      </div>

      {/* Create Post & Search */}
      <div className="create-search-container">
        <CreatePost onPostCreated={post => { setMyPosts(prev => [post, ...prev]); setRecommendations(prev => [post, ...prev]); }} />
        <form onSubmit={handleSearch} className="search-form">
          <input type="text" placeholder="Search for a destination..." value={search} onChange={e => setSearch(e.target.value)} />
          <button type="submit">Search</button>
        </form>
      </div>

      {/* My Posts */}
      <h3 className="genz-subheading">My Posts 📝</h3>
      <div className="recommendation-cards">
        {myPosts.length === 0 && <p>You haven't posted any trips yet!</p>}
        {myPosts.map((rec, i) => (
          <div key={rec.id || i} className="rec-card">
            <h4>{rec.destination || "Unknown Place"}</h4>
            <p>{rec.description || "No description available."}</p>
            {rec.travel_date && <small>Travel Date: {rec.travel_date}</small>}
          </div>
        ))}
      </div>

      {/* Search Results */}
      {searchResults.length > 0 && (
        <>
          <h3 className="genz-subheading">Search Results 🔍</h3>
          <div className="recommendation-cards">
            {searchResults.map((rec, i) => (
              <div key={rec.id || i} className="rec-card">
                <h4>{rec.place || rec.destination || "Unknown Place"}</h4>
                <small>Posted by: {rec.user_name}</small>
                <p>{rec.description || "No description available."}</p>
                {rec.travel_date && <small>Travel Date: {rec.travel_date}</small>}
                <button onClick={() => openChat(rec.id)}>Chat</button>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Recommended Trips */}
      {recommendations.length > 0 && (
        <>
          <h3 className="genz-subheading">Trips & Posts ✨</h3>
          <div className="recommendation-cards">
            {recommendations.map((rec, i) => (
              <div key={rec.id || i} className="rec-card">
                <h4>{rec.place || rec.destination || "Unknown Place"}</h4>
                {rec.user_name && <small>Posted by: {rec.user_name}</small>}
                <p>{rec.description || "No description available."}</p>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Active Chat Window */}
      {activeChatPost && (
        <div className="chat-window">
          <h4>Chat for Post #{activeChatPost}</h4>
          <div className="chat-messages">
            {chatMessages.map((msg, i) => (
              <div key={i}><strong>{msg.sender_name}:</strong> {msg.message}</div>
            ))}
          </div>
          <input type="text" placeholder="Type message..." value={newMessage} onChange={e => setNewMessage(e.target.value)} />
          <button onClick={sendMessage}>Send</button>
        </div>
      )}
    </div>
  );
}

export default Main;
