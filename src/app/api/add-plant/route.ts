import { NextResponse } from "next/server";
import { DynamoDBClient, PutItemCommand } from "@aws-sdk/client-dynamodb";

// Configure DynamoDB
// DynamoDB configuration
const dynamoDB = new DynamoDBClient({
  region: process.env.AWS_REGION,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
});

export async function POST(req: Request) {
  try {
    const plant = await req.json();

    if (!plant || !plant.plantName) {
      return NextResponse.json({ error: "Invalid plant data" }, { status: 400 });
    }

    const params = {
      TableName: "plantData",
      Item: {
        plantName: { S: plant.plantName.S },
        moisture: { S: "0" },
        sunlight: { S: "0" },
        temperature: { S: "0" },
        humidity: { S: "0" },
        led: { S: "00FF00" },
        battery: {S: "0" }
      },
    };

    await dynamoDB.send(new PutItemCommand(params));
    return NextResponse.json({ message: "Plant added successfully" });
  } catch (error: unknown) {
    let errorMessage = "An unknown error occurred";

    if (error instanceof Error) {
      errorMessage = error.message;
    }

    return NextResponse.json({ error: errorMessage }, { status: 500 });
  }
}
