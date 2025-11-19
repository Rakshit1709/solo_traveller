import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./login.css";

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false); // optional loading state

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true); // start loading
    console.log("Attempting login for:", email);

    try {
      const response = await fetch("http://localhost:5000/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();
      console.log("Login response:", data);

      if (response.status === 200) {
        alert(`Welcome, ${data.name}!`);
        localStorage.setItem("user", JSON.stringify(data));

        console.log("Redirecting to /main");
        navigate("/main"); // redirect to main page
      } else {
        console.error("Login failed:", data.message);
        alert(data.message || "Login failed. Check credentials.");
      }
    } catch (error) {
      console.error("Error during login:", error);
      alert("Something went wrong. Try again.");
    } finally {
      setLoading(false); // stop loading
    }
  };

  const goToSignup = () => {
    console.log("Navigating to /signup");
    navigate("/signup");
  };

  return (
    <div className="login-container">
      <form className="login-form" onSubmit={handleLogin}>
        <h2>Login</h2>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? "Logging in..." : "Login"}
        </button>
        <p>
          Don't have an account?{" "}
          <span className="signup-link" onClick={goToSignup}>
            Sign Up
          </span>
        </p>
      </form>
    </div>
  );
}

export default Login;
