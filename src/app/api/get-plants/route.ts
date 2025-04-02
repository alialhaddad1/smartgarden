import { NextResponse } from "next/server";
import { DynamoDBClient, ScanCommand } from "@aws-sdk/client-dynamodb";

// DynamoDB configuration
const dynamoDB = new DynamoDBClient({ region: "us-east-2" });

export async function GET() {
  const params = {
    TableName: "plantData",
  };

  try {
    const data = await dynamoDB.send(new ScanCommand(params));
    const plants = data.Items?.map((item) => ({
      plantName: item.plantName.S,
      moisture: item.moisture.S,
      sunlight: item.sunlight.S,
      temperature: item.temperature.S,
      humidity: item.humidity.S,
      led: item.led.S,
      battery: item.battery.S,
    })) || [];

    return NextResponse.json(plants);
  } catch (error: unknown) {
    let errorMessage = "An unknown error occurred";

    if (error instanceof Error) {
      errorMessage = error.message;
    }

    return NextResponse.json({ error: errorMessage }, { status: 500 });
  }
}
