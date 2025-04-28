import { NextRequest, NextResponse } from "next/server";
import { DynamoDBClient, GetItemCommand } from "@aws-sdk/client-dynamodb";

const dynamoDB = new DynamoDBClient({
  region: "us-east-2",
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
});

export const GET = async (req: NextRequest) => {
  const plantName = req.nextUrl.searchParams.get("plantName");

  if (req.headers.get("x-api-key") !== process.env.ESP_API_KEY) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  if (!plantName) {
    return NextResponse.json({ error: "Missing plantName query parameter" }, { status: 400 });
  }

  try {
    const command = new GetItemCommand({
      TableName: "plantData",
      Key: { plantName: { S: plantName } },
    });

    const response = await dynamoDB.send(command);

    if (!response.Item) {
      return NextResponse.json({ error: "Plant not found" }, { status: 404 });
    }

    const data = {
      plantName: response.Item.plantName?.S,
      moisture: response.Item.moisture?.S,
      sunlight: response.Item.sunlight?.S,
      temperature: response.Item.temperature?.S,
      humidity: response.Item.humidity?.S,
      led: response.Item.led?.S,
      battery: response.Item.battery?.S,
    };

    return NextResponse.json({ success: true, data }, { status: 200 });
  } catch (err) {
    console.error("DynamoDB read error:", JSON.stringify(err, null, 2));
    return NextResponse.json({ error: "DynamoDB read failed" }, { status: 500 });
  }
};
