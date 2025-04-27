import "./App.css";
import Form from "./components/form";
import axios from "axios";
import React, { useState, useEffect } from "react";

function App() {
  // const [data, setData] = useState(null);
  // const [loading, setLoading] = useState(true);
  // useEffect(() => {
  //   async function getData() {
  //     try {
  //       const response = await axios.get("http://localhost:3000");
  //       console.log("Response:", response.data);
  //       setData(response.data); // Save data to state
  //     } catch (error) {
  //       console.error("Error fetching data:", error);
  //     } finally {
  //       setLoading(false); // Set loading to false once the request is complete
  //     }
  //   }

  //   getData();
  // }, []); // Empty dependency array ensures it runs only once when the component mounts

  return (
    <div>
      <Form />
    </div>
  );
}

export default App;
