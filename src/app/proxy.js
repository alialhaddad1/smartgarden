import express from "express";
import fetch from "node-fetch";

const app = express();
const PORT = 3001;

const VERCEL_URL = "https://smartgarden.vercel.app/api/update-plant";
const API_KEY = "cb9e9bc88da7b9c97eee595a4bab04ef6a8709cd97f5f573d9509c375ac58267"; // same one used in Vercel env vars

app.use(express.json());

app.post("/update-plant", async (req, res) => {
  try {
    const response = await fetch(VERCEL_URL, {
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
    console.error("Proxy error:", err);
    res.status(500).json({ error: "Proxy failed" });
  }
});

app.listen(PORT, () => {
  console.log(`🌱 Proxy server running at http://localhost:${PORT}/update-plant`);
});
