"use client";
import Image from "next/image";
import Link from "next/link";
import React from "react";
import { useEffect, useState } from "react";

// THERE NEEDS TO BE A WAY TO DELETE PLANTS FROM PLANTDATA ON THIS PAGE AS WELL

// Define the structure of a plant item from DynamoDB
type Plant = {
  plantName: string;
  moisture: string;
  sunlight: string;
  temperature: string;
};

export default function MonitorPage() {
  const [plants, setPlants] = useState<Plant[]>([]);
  const [selectedPlant, setSelectedPlant] = useState<Plant | null>(null);

  // Fetch plants from the API
  useEffect(() => {
    const fetchPlants = async () => {
      try {
        const res = await fetch("/api/get-plants");
        const data = await res.json();
        setPlants(data);
      } catch (error) {
        console.error("Error fetching plants:", error);
      }
    };

    fetchPlants();

    // Poll every 5 seconds to get real-time updates
    const interval = setInterval(fetchPlants, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">Your Plants</h1>
      <p>This page allows users to view their plants.</p>
      <nav>
        <ul>
          <li>
            <Link href="/">Home Page</Link>
          </li>
        </ul>
      </nav>

      {/* Dropdown menu */}
      <select
        className="border p-2 rounded w-full"
        onChange={(e) => {
          const plant = plants.find((p) => p.plantName === e.target.value) || null;
          setSelectedPlant(plant);
        }}
      >
        <option value="">Select a plant</option>
        {plants.map((plant) => (
          <option key={plant.plantName} value={plant.plantName}>
            {plant.plantName}
          </option>
        ))}
      </select>

      {/* Show details of the selected plant */}
      {selectedPlant && (
        <div className="mt-4 p-4 border rounded">
          <h2 className="text-lg font-semibold">{selectedPlant.plantName}</h2>
          <p>Moisture Needs: {selectedPlant.moisture}</p>
          <p>Sunlight Needs: {selectedPlant.sunlight}</p>
          <p>Temperature Range: {selectedPlant.temperature}</p>
        </div>
      )}
    </div>
  );
}