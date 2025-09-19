import React, { useState } from "react";
import LoginPage from "./LoginPage";
import LandingPage from "./LandingPage";
import AboutUs from "./aboutus";
import SignUpPage from "./SignUpPage";

const App = () => {
  const [currentPage, setCurrentPage] = useState("landing"); 

  const handleUserLogin = () => {
    setCurrentPage("home");
  };

  const handleSignUp = (signUpData) => {
    console.log("Sign up data:", signUpData);
    setCurrentPage("login");
  };

  const renderCurrentPage = () => {
    switch(currentPage) {
      case "landing":
        return (
          <LandingPage 
            onSignInClick={() => setCurrentPage("login")}
            onAboutClick={() => setCurrentPage("about")}
          />
        );
      
      case "about":
        return (
          <AboutUs onBack={() => setCurrentPage("landing")} />
        );
      
      case "login":
        return (
          <LoginPage 
            onLogin={handleUserLogin}
            onSignUpClick={() => setCurrentPage("signup")}
          />
        );
      
      case "signup":
        return (
          <SignUpPage 
            onSignUp={handleSignUp}
            onBackToLogin={() => setCurrentPage("login")}
          />
        );
      
      case "home":
        return (
          <div style={{ padding: "40px", textAlign: "center", color: "white", background: "#0f172a", minHeight: "100vh" }}>
            <h1>Welcome! You are logged in.</h1>
            <button 
              onClick={() => setCurrentPage("landing")}
              style={{
                marginTop: "20px",
                padding: "12px 24px",
                background: "#36dad6",
                color: "black",
                border: "none",
                borderRadius: "8px",
                cursor: "pointer",
                fontWeight: "600"
              }}
            >
              Back to Home
            </button>
          </div>
        );
      
      default:
        return (
          <LandingPage 
            onSignInClick={() => setCurrentPage("login")}
            onAboutClick={() => setCurrentPage("about")}
          />
        );
    }
  };

  return (
    <div className="App">
      {renderCurrentPage()}
    </div>
  );
};

export default App;