import { NextRequest, NextResponse } from "next/server";
import { DynamoDBClient, UpdateItemCommand } from "@aws-sdk/client-dynamodb";

const dynamoDB = new DynamoDBClient({
  region: "us-east-2",
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
});

export const POST = async (req: NextRequest) => {
  if (req.headers.get("x-api-key") !== process.env.ESP_API_KEY) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = await req.json();
  const {
    plantName,
    microMoisture,
    microSun,
    microTemp,
    microHumid,
    microLED,
    microBattery,
  } = body;

  if (!plantName) {
    return NextResponse.json({ error: "Missing plantName" }, { status: 400 });
  }

  try {
    const command = new UpdateItemCommand({
      TableName: "plantData", // ✅ Correct table name
      Key: { plantName: { S: plantName } },
      UpdateExpression:
        "SET moisture = :m, sunlight = :s, temperature = :t, humidity = :h, led = :l, battery = :b",
      ExpressionAttributeValues: {
        ":m": { S: microMoisture.toString() },
        ":s": { S: microSun.toString() },
        ":t": { S: microTemp.toString() },
        ":h": { S: microHumid.toString() },
        ":l": { S: microLED },
        ":b": { S: microBattery.toString() },
      },
    });

    await dynamoDB.send(command);
    return NextResponse.json({ success: true }, { status: 200 });
  } catch (err) {
    console.error(err);
    return NextResponse.json({ error: "DynamoDB update failed" }, { status: 500 });
  }
};
