import express from "express";
import fetch from "node-fetch";

const app = express();
const PORT = 3001;

const VERCEL_BASE_URL = "https://smartgarden.vercel.app/api";
const API_KEY = "cb9e9bc88da7b9c97eee595a4bab04ef6a8709cd97f5f573d9509c375ac58267";

app.use(express.json());

// Proxy POST requests to update-plant
app.post("/update-plant", async (req, res) => {
  try {
    const response = await fetch(`${VERCEL_BASE_URL}/update-plant`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": API_KEY,
      },
      body: JSON.stringify(req.body),
    });

    const data = await response.json();
    res.status(response.status).json(data);
  } catch (err) {
    console.error("Proxy error (update-plant):", err);
    res.status(500).json({ error: "Proxy failed on update-plant" });
  }
});

// Proxy GET requests to read-plant
app.get("/read-plant", async (req, res) => {
  try {
    const response = await fetch(`${VERCEL_BASE_URL}/read-plant`, {
      method: "GET",
      headers: {
        "x-api-key": API_KEY,
      },
    });

    const data = await response.json();
    res.status(response.status).json(data);
  } catch (err) {
    console.error("Proxy error (read-plant):", err);
    res.status(500).json({ error: "Proxy failed on read-plant" });
  }
});

app.listen(PORT, () => {
  console.log(`🌱 Proxy server running at http://localhost:${PORT}`);
  console.log(`- POST to http://localhost:${PORT}/update-plant`);
  console.log(`- GET from http://localhost:${PORT}/read-plant`);
});