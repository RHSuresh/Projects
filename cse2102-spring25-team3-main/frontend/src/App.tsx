import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./components/Home";
import Login from "./components/Login"
import SignUp from "./components/SignUp"
import Logout from "./components/Logout"
import "./App.css";
import PetsList from "./components/PetsList";
import Favorites from "./components/Favorites";
import AppointmentsList from "./components/AppointmentsList";
import Adopt from "./components/Adopt";


const App: React.FC = () => {
  return (
    <Router>
      <div>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/logout" element={<Logout />} />
          <Route path="/pets" element={<PetsList />} />
          <Route path="/favorites" element={<Favorites />} />
          <Route path="/appointments" element={<AppointmentsList />} />
          <Route path="/adopt-request" element={<Adopt />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
