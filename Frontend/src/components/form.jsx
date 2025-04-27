import React, { useState } from "react";
import "./form.css";
import logo from "./logo.png"; // Import logo (adjust the path based on your file structure)

const Form = () => {
  const [input, setInput] = useState(""); // User input for the first textbox
  const [response, setResponse] = useState(""); // Response input for the second textbox
  const [messages, setMessages] = useState([]);
  const [isDarkMode, setIsDarkMode] = useState(false); // State for dark mode

  const handleInputChange = (event) => {
    setInput(event.target.value);
  };

  const handleResponseChange = (event) => {
    setResponse(event.target.value); // Handle change for response textbox
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (input.trim() === "") return;
    setMessages([...messages, { text: input, isUser: true }]);
    setInput("");
  };

  const handleResponseSubmit = (event) => {
    event.preventDefault();
    if (response.trim() === "") return;
    setMessages([...messages, { text: response, isUser: false }]); // Add response message
    setResponse(""); // Clear the response input after submission
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

      {/* User input textbox */}
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

      {/* Response textbox */}
      <form className="input-form" onSubmit={handleResponseSubmit}>
        <input
          type="text"
          value={response}
          onChange={handleResponseChange}
          placeholder="Response"
          className="input-field"
        />
        <button type="submit" className="submit-btn">
          Respond
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
