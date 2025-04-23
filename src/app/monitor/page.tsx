"use client";
import React from "react";
import { useEffect, useState } from "react";
import { Button } from 'antd';
//import { unmarshall } from "@aws-sdk/util-dynamodb";
//import { DynamoDBClient, ScanCommand } from "@aws-sdk/client-dynamodb";
import '../styles.css';

/* 
1. Implement LED light change algorithm; you write this value to the database
  // Low battery = red
  // No change needed = green
  // Change needed = orange
  // Check updated values of battery from database to change to red
*/
/*
const dynamoDB = new DynamoDBClient({
  region: "us-east-2",
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
});
*/
// Define the structure for ThingSpeak data
type ThingSpeakEntry = {
  created_at: string;
  field1?: number | null;
  field2?: number | null;
  field3?: number | null;
  field4?: string | null; // Keep field4 as a string for hex codes
  field5?: number | null;
  field6?: number | null;
  field7?: number | null;
  field8?: number | null;
};

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
  const [thingSpeakData, setThingSpeakData] = useState<Record<string, ThingSpeakEntry>>({});
  const channel = [{ id: "2831003", apiKey: "XB89AZ0PZ5K91BV2" }];

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
      //setPlants(plants.filter((plant) => plant.plantName !== plantName)); // Update UI
      setSelectedPlant(null); // Clear selection
    } else {
      alert("Error removing plant. Try again.");
    }
  };

  const fetchThingSpeakData = async () => {
    try {
      const results: Record<string, ThingSpeakEntry> = {};
      
      await Promise.all(
        channel.map(async (channel) => {
          const response = await fetch(
            //`https://api.thingspeak.com/channels/${channel.id}/feeds.json?api_key=${channel.apiKey}&results=1`
            `https://api.thingspeak.com/channels/${channel.id}/feeds.json?results=1&api_key=${channel.apiKey}`
          );
          const data = await response.json();
  
          console.log("Raw ThingSpeak API response:", data); // Debugging
  
          if (data.feeds && data.feeds.length > 0) {
            const entry = data.feeds[0]; 
            
            results[channel.id] = {
              created_at: entry.created_at,
              field1: entry.field1 ? Number(entry.field1) : null,
              field2: entry.field2 ? Number(entry.field2) : null,
              field3: entry.field3 ? Number(entry.field3) : null,
              field4: entry.field4 ?? null, // Keep as string for hex codes
              field5: entry.field5 ? Number(entry.field5) : null,
              field6: entry.field6 ? Number(entry.field6) : null,
              field7: entry.field7 ? Number(entry.field7) : null,
              field8: entry.field8 ? Number(entry.field8) : null,
            };
          }
        })
      );
  
      console.log("Processed ThingSpeak Data:", results); // Debugging
      setThingSpeakData(results);
    } catch (error) {
      console.error("Error fetching ThingSpeak data:", error);
    }
  };
  /*
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
  */
  const fetchPlantStatus = async () => {
    const res = await fetch("/api/get-plant-status");
    return res.json();
  };
  
  useEffect(() => {
    const loadStatus = async () => {
      const statuses = await fetchPlantStatus();
      console.log("Plant statuses:", setPlants); // This makes it “used”
      console.log("Plant statuses:", plantStatuses);
      console.log("Plant statuses:", setPlantStatuses);
      console.log("Plant statuses:", statuses);
      // Optionally store it later if needed
    };

    loadStatus();
  
    fetchPlantStatus();

    fetchThingSpeakData();
  
    const interval_1 = setInterval(fetchThingSpeakData, 10000);
    const interval_2 = setInterval(loadStatus, 10000);
  
    return () => {
      clearInterval(interval_1);
      clearInterval(interval_2);
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
              const match = (data.result as PlantStatus[]).find((p) => p.plantName === plant.plantName);
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
  
          {/* Remove Plant Button */}
          <Button
            onClick={() => removePlant(selectedPlant.plantName)}
            className="ant-btn-primary mt-4"
          >
            Remove from Collection
          </Button>
        </div>
      )}
  
      {/* ThingSpeak Data Section - Always Visible */}
      <div className="mt-6 p-4 border rounded">
        <h2 className="text-lg font-semibold">Sensor Data (From ThingSpeak)</h2>
        {Object.keys(thingSpeakData).length > 0 ? (
          Object.entries(thingSpeakData).map(([channelId, entry]) => (
            <div key={channelId} className="mt-2 p-2 border rounded">
              <p>
                <strong>Channel ID:</strong> {channelId}
              </p>
              <p>
                <strong>Timestamp:</strong>{" "}
                {new Date(entry.created_at).toLocaleString()}
              </p>
              <p>
                <strong>Temperature (F):</strong>{" "}
                {entry.field1 !== null ? entry.field1 : "N/A"}
              </p>
              <p>
                <strong>Moisture (%):</strong>{" "}
                {entry.field2 !== null ? entry.field2 : "N/A"}
              </p>
              <p>
                <strong>Sunlight (lux):</strong>{" "}
                {entry.field3 !== null ? entry.field3 : "N/A"}
              </p>
              <p>
                <strong>LED Color:</strong> {entry.field4 ?? "N/A"}
              </p>
              <p>
                <strong>Humidity (%):</strong>{" "}
                {entry.field5 !== null ? entry.field5 : "N/A"}
              </p>
              <p>
                <strong>Battery Life (%):</strong>{" "}
                {entry.field6 !== null ? entry.field6 : "N/A"}
              </p>
            </div>
          ))
        ) : (
          <p>Loading ThingSpeak data...</p>
        )}
      </div>
    </div>
  );
}