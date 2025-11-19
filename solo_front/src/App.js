import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";


import Home from "./home";
import Login from "./login";
import Signup from "./signup";
import Hobbies from "./hobby";
import Main from "./main";
import Chat from "./chat";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/Hobbies" element={<Hobbies />} />
        <Route path="/main" element={<Main />} />
        <Route path = "/chat" element={<Chat />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
