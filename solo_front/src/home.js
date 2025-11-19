import React from "react";
import { useNavigate } from "react-router-dom";
import "./home.css"; 

function Home() {
  const navigate = useNavigate();

  const goToLogin = () => {
    navigate("/login"); 
  };

  return (
    <div className="home-container">
      <div className="overlay">
        <h1>Planning to explore the unexplored?</h1>
        <h3>Plan. Pack. Slay. Repeat</h3>
        <button onClick={goToLogin}>Login</button>
      </div>
    </div>
  );
}

export default Home;
