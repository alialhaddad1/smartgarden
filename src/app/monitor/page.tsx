"use client";
import React from "react";
import { useEffect, useState } from "react";
import { Button } from 'antd';
import '../styles.css';

// Define the structure of a plant item from DynamoDB
type Plant = {
  plantName: string;
  moisture: string;
  sunlight: string;
  temperature: string;
  humidity: string;
  led: string;
  battery: string;
};

interface Status {
  plantName: string;
  status: { status: string; message?: string }[];
};

type PlantStatus = {
  plantName: string;
  status: {
    status: string;
    message?: string;
  }[];
};

export default function MonitorPage() {
  const [plants, setPlants] = useState<Plant[]>([]);
  const [selectedPlant, setSelectedPlant] = useState<Plant | null>(null);
  const [plantStatuses, setPlantStatuses] = useState<Status[]>([]);
  const [selectedStatus, setSelectedStatus] = useState<{ status: string; message?: string }[] | null>(null);

  // Remove plant function
  const removePlant = async (plantName: string) => {
    const confirmed = window.confirm(`Are you sure you want to remove "${plantName}" from your collection?`);
    if (!confirmed) return;
  
    const res = await fetch("/api/remove-plants", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ plantName }),
    });
  
    if (res.ok) {
      alert(`${plantName} removed from your collection.`);
      setSelectedPlant(null); // Clear selection
    } else {
      alert("Error removing plant. Try again.");
    }
  };
  
  const fetchPlants = async () => {
    try {
      const res = await fetch("/api/get-plants");
      const data = await res.json();
      if (!Array.isArray(data)) {
        console.error("Unexpected response format:", data);
        setPlants([]); // Ensure plants is always an array
        return;
      }
      setPlants(data);
    } catch (error) {
      console.error("Error fetching plants:", error);
      setPlants([]); // Prevents crashing by ensuring an empty array
    }
  };
  
  const fetchPlantStatus = async () => {
    const res = await fetch("/api/get-plant-status");
    return res.json();
  };
  
  useEffect(() => {
    const loadStatus = async () => {
      const statuses = await fetchPlantStatus();
      setPlantStatuses(statuses.result); 
      console.log("Plant statuses:", setPlants); // This makes it “used”
      console.log("Plant statuses:", plantStatuses);
      console.log("Plant statuses:", setPlantStatuses);
      console.log("Plant statuses:", statuses);
    };
  
    fetchPlants(); 
    loadStatus();
  
    const interval = setInterval(loadStatus, 10000);
  
    return () => {
      clearInterval(interval);
    };
  }, []);
  
  return (
    <div className="p-4">
      <h1 className="ant-typography">Your Plants</h1>
      <h2 className="text-xl font-bold mb-4">
        This page allows users <br />to view their saved plants.
      </h2>
  
      <nav>
        <ul>
          <li>
            <Button className="ant-btn-primary" href="/">
              Home Page
            </Button>
          </li>
        </ul>
      </nav>
  
      {/* Dropdown menu */}
      <select
        className="border p-2 rounded w-full"
        style={{ color: "black" }}
        onChange={async (e) => {
          const plant = plants.find((p) => p.plantName === e.target.value) || null;
          setSelectedPlant(plant);
          setSelectedStatus(null); // reset while loading
        
          if (plant) {
            try {
              const res = await fetch("/api/get-plant-status");
              const data = await res.json();
              const match = (data.result as PlantStatus[]).find((p: PlantStatus) => p.plantName === plant.plantName);
              setSelectedStatus(match?.status || []);
            } catch (err) {
              console.error("Failed to fetch status:", err);
              setSelectedStatus([{ status: "error", message: "Could not load plant status." }]);
            }
          }
        }}
      >
        <option value="">Select a plant</option>
        {plants.map((plant) => (
          <option key={plant.plantName} value={plant.plantName}>
            {plant.plantName}
          </option>
        ))}
      </select>
  
      {/* Show status for selected plant */}
      {selectedPlant && (
        <div className="mt-4 p-4 border rounded shadow">
          <h2 className="text-lg font-semibold">{selectedPlant.plantName}</h2>

          <div className="mt-2">
            <h3 className="font-semibold mb-1">Status:</h3>
            {Array.isArray(selectedStatus) && selectedStatus.length > 0 ? (
              <ul className="list-disc list-inside">
                {selectedStatus.map((s, idx) => (
                  <li key={idx}>
                    <strong>{s.status}</strong>{s.message ? ` — ${s.message}` : ""}
                  </li>
                ))}
              </ul>
            ) : (
              <p>Loading or no status available.</p>
            )}
          </div>

          {/* Show attributes for selected plant */}
          <div className="mt-4">
            <h3 className="font-semibold mb-1">Current Attributes:</h3>
            <ul className="list-disc list-inside">
              <li>Moisture: {selectedPlant.moisture}</li>
              <li>Sunlight: {selectedPlant.sunlight}</li>
              <li>Temperature: {selectedPlant.temperature}</li>
              <li>Humidity: {selectedPlant.humidity}</li>
              <li>LED Status: {selectedPlant.led}</li>
              <li>Battery: {selectedPlant.battery}</li>
            </ul>
          </div>

          <Button
            onClick={() => removePlant(selectedPlant.plantName)}
            className="ant-btn-primary mt-4"
          >
            Remove from Collection
          </Button>
        </div>
      )}
    </div>
  );
}