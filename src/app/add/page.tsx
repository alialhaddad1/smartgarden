"use client";
import Image from "next/image";
import Link from "next/link";
import React, { useState } from "react";
import SearchBar from "../components/searchBar"; // Import the search bar component

// Define the structure of a plant item from DynamoDB
interface Plant {
  plantName: { S: string };
  moisture?: { S: string };
  sunlight?: { S: string };
  temperature?: { S: string };
}

export default function AddPage() {
  const [results, setResults] = useState<Plant[]>([]); // Define type for results array

  const handleSearch = async (query: string) => {
    if (!query.trim()) return;

    const res = await fetch(`/api/search?q=${query}`);
    const data: Plant[] = await res.json(); // Explicitly define API response type

    setResults(data || []); // Update results with response from API (|| [] may not be correct)
  };

  // Function to add plant to plantData
  const addToPlantData = async (plant: any) => {
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
      <h1>Add</h1>
      <p>This page allows users to add plants to their collection.</p>
      <nav>
        <ul>
          <li>
            <Link href="/">Home Page</Link>
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