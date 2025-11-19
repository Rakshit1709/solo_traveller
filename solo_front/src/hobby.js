import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./hobby.css"; // CSS for styling

function Hobbies() {
  const navigate = useNavigate();
  const [hobbies, setHobbies] = useState([]);
  const [selected, setSelected] = useState([]);

  const user = JSON.parse(localStorage.getItem("user")); // logged-in user

  useEffect(() => {
    fetch("http://localhost:5000/api/hobbies")
      .then((res) => res.json())
      .then((data) => setHobbies(data))
      .catch((err) => console.error(err));
  }, []);

  const toggleHobby = (id) => {
    if (selected.includes(id)) {
      setSelected(selected.filter((h) => h !== id));
    } else {
      setSelected([...selected, id]);
    }
  };

  const handleSubmit = async () => {
    if (selected.length === 0) {
      alert("Select at least one hobby!");
      return;
    }

    try {
      const response = await fetch("http://localhost:5000/api/user_hobbies", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: user.id, hobbies: selected }),
      });

      const data = await response.json();
      if (response.status === 201) {  
        alert("Hobbies saved! Now we can recommend places.");
        navigate("/login"); 
      } else {
        alert(data.message || "Failed to save hobbies.");
      }
    } catch (error) {
      console.error(error);
      alert("Something went wrong.");
    }
  };

  return (
    <div className="hobbies-container">
      <h2>Select Your Interests</h2>
      <div className="hobbies-grid">
        {hobbies.map((hobby, index) => (
          <div
            key={hobby.id}
            className={`hobby-card ${selected.includes(hobby.id) ? "selected" : ""}`}
            onClick={() => toggleHobby(hobby.id)}
          >
            <div className="hobby-number">{index + 1}</div>
            <div className="hobby-name">{hobby.name}</div>
          </div>
        ))}
      </div>
      <button className="continue-btn" onClick={handleSubmit}>Continue</button>
    </div>
  );
}

export default Hobbies;
