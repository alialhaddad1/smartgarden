"use client";
import React, { useState } from "react";
import SearchBar from "../components/searchBar"; // Import the search bar component
import { Button } from 'antd';
//import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import '../styles.css';

// ENTRIES NEED TO BE FORMATTED AS STRINGS? 

// const ESP32_IP = "192.168.1.100"; // Predefined ESP32 IP address
// const UPDATE_INTERVAL = 10000; // 10 seconds

// Define the structure of a plant item from DynamoDB
interface Plant {
  plantName: { S: string };
  moisture?: { S: string };
  sunlight?: { S: string };
  temperature?: { S: string };
  humidity?: { S: string };
  led: { S: string };
  battery?: { S: string };
}

export default function AddPage() {
  const [results, setResults] = useState<Plant[]>([]); // Define type for results array

  const handleSearch = async (query: string) => {
    if (!query.trim()) return;

  try {
    const res = await fetch(`/api/search?q=${query}`);
    const result = await res.json();

    if (Array.isArray(result)) {
      const lower = query.toLowerCase();
      setResults(result.filter(
        (p) => p?.plantName?.S?.toLowerCase().includes(lower)
      ));
    } else {
      setResults([]);
      console.error("Unexpected search result:", result);
    }
  } catch (err) {
    console.error("Search error:", err);
    setResults([]);
  }
  };  

  // Function to add plant to plantData
  const addToPlantData = async (plant: Plant) => {
    const res = await fetch("/api/add-plant", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(plant),
    });

    if (res.ok) {
      alert(`${plant.plantName.S} added to your collection!`);
    } else {
      alert("Error adding plant. Try again.");
    }
  };

  return (
    <div className="p-4">
      <h1 className="ant-typography">Add</h1>
      <h2 className="text-xl font-bold mb-4">This page allows users <br></br>to add plants <br></br>to their collection.</h2>
      <nav>
        <ul>
            <li>
              <Button className="ant-btn-primary" href="/">Home Page</Button>
            </li>
        </ul>
      </nav>

      <h1 className="text-xl font-bold mb-4">Search for a Plant</h1>

      {/* Use the SearchBar component */}
      <SearchBar onSearch={handleSearch} />

      {/* Display results */}
      <div className="mt-4">
        {results.length > 0 ? (
          results.map((plant, index) => (
            <div key={index} className="p-2 border-b">
              <h2 className="text-lg font-semibold">{plant.plantName.S}</h2>
              <p>Moisture Needs: {plant.moisture?.S || "N/A"}</p>
              <p>Sunlight Needs: {plant.sunlight?.S || "N/A"}</p>
              <p>Temperature Range: {plant.temperature?.S || "N/A"}</p>
              <button
                onClick={() => addToPlantData(plant)}
                className="mt-2 p-2 bg-blue-500 text-white rounded"
              >
                Add to Collection
              </button>
            </div>
          ))
        ) : (
          <p>No results found.</p>
        )}
      </div>
    </div>
  );
}