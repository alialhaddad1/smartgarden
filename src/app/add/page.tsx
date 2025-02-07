"use client";
import Image from "next/image";
import Link from "next/link";
import React from "react";
import { useState } from "react";

export default function AddPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    const res = await fetch(`/api/search?query=${query}`);
    const data = await res.json();
    
    setResults(data); // Update results with response from API
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
      
      <input
        type="text"
        placeholder="Enter plant name..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="border p-2 rounded w-full"
      />
      
      <button
        onClick={handleSearch}
        className="mt-2 p-2 bg-green-500 text-black rounded"
      >
        Search
      </button>

      {/* Display results */}
      <div className="mt-4">
        {results.length > 0 ? (
          results.map((plant, index) => (
            <div key={index} className="p-2 border-b">
              <h2 className="text-lg font-semibold">{"One"}</h2> {/*plant.name*/}
              <p>Moisture Needs: {"Two"}</p> {/*plant.moisture*/}
              <p>Sunlight Needs: {"Three"}</p> {/*plant.sunlight*/}
              <p>Temperature Range: {"Four"}</p> {/*plant.temperature*/}
            </div>
          ))
        ) : (
          <p>No results found.</p>
        )}
      </div>
    </div>
  );
}