import { DynamoDBClient, UpdateItemCommand } from "@aws-sdk/client-dynamodb";

const client = new DynamoDBClient({ region: "us-east-2" });

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).end("Method not allowed");
  if (req.headers["x-api-key"] !== process.env.ESP_API_KEY) {
    return res.status(401).json({ error: "Unauthorized" });
  }

  const { plantName, microMoisture, microSun, microTemp, microHumid, microLED, microBattery } = req.body;

  if (!plantName) return res.status(400).json({ error: "Missing plantName" });

  try {
    const command = new UpdateItemCommand({
      TableName: "YourTableName",
      Key: { plantName: { S: plantName } },
      UpdateExpression: "SET moisture = :m, sunlight = :s, temperature = :t, humidity = :h, led = :l, battery = :b",
      ExpressionAttributeValues: {
        ":m": { S: microMoisture },
        ":s": { S: microSun },
        ":t": { S: microTemp },
        ":h": { S: microHumid },
        ":l": { S: microLED },
        ":b": { S: microBattery },
      },
    });
    await client.send(command);
    res.status(200).json({ success: true });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "DynamoDB update failed" });
  }
}