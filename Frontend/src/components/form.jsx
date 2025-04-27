import React, { useState } from "react";
import "./form.css";
import logo from "./logo.png"; // Import logo (adjust the path based on your file structure)

const Form = () => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [isDarkMode, setIsDarkMode] = useState(false); // State for dark mode

  const handleInputChange = (event) => {
    setInput(event.target.value);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (input.trim() === "") return;
    setMessages([...messages, { text: input, isUser: true }]);
    setInput("");
  };

  const toggleTheme = () => {
    setIsDarkMode((prevMode) => !prevMode); // Toggle the dark mode
  };

  return (
    <div className={`chat-container ${isDarkMode ? "dark" : ""}`}>
      {/* Display Logo */}
      <div className="logo-container">
        <img src={logo} alt="Logo" className="logo" />
      </div>

      <div className="messages">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.isUser ? "user" : "bot"}`}
          >
            {message.text}
          </div>
        ))}
      </div>
      <form className="input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={handleInputChange}
          placeholder="Type a message..."
          className="input-field"
        />
        <button type="submit" className="submit-btn">
          Send
        </button>
      </form>
      <div className="buttons-container">
        <button className="theme-toggle-btn" onClick={toggleTheme}>
          {isDarkMode ? "Light Mode" : "Dark Mode"}
        </button>
        <button
          className="clear-btn"
          onClick={() => setMessages([])} // Clear messages when pressed
        >
          Clear
        </button>
      </div>
    </div>
  );
};

export default Form;
