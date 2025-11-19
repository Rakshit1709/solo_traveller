import React, { useState } from "react";
import "./createpost.css";

function CreatePost({ onPostCreated }) {
  const [destination, setDestination] = useState("");
  const [description, setDescription] = useState("");
  const [travelDate, setTravelDate] = useState("");
  const user = JSON.parse(localStorage.getItem("user")); // logged-in user

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!destination || !description) {
      alert("Fill in both destination and description!");
      return;
    }

    try {
      const res = await fetch("http://localhost:5000/api/solo-traveller", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: user.id,
          destination,
          description,
          travelDate,
        }),
      });

      const newPost = await res.json();
      if (onPostCreated) onPostCreated(newPost);

      // Clear inputs
      setDestination("");
      setDescription("");
      setTravelDate("");
    } catch (err) {
      console.error("Error creating post:", err);
      alert("Failed to create post. Try again!");
    }
  };

  return (
    <div className="create-post-container">
      <h3 className="genz-heading">🚀 Share Your Trip</h3>
      <form onSubmit={handleSubmit} className="create-post-form">
        <input
          className="genz-input"
          type="text"
          placeholder="Where are you heading? (Destination)"
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
        />
        <textarea
          className="genz-textarea"
          placeholder="Drop your thoughts here..."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        ></textarea>
        <input
          className="genz-input"
          type="date"
          value={travelDate}
          onChange={(e) => setTravelDate(e.target.value)}
        />
        <button className="genz-button" type="submit">
          ✨ Post
        </button>
      </form>
    </div>
  );
}

export default CreatePost;
