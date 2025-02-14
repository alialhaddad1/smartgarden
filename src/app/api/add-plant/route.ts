import { NextResponse } from "next/server";
import { DynamoDBClient, PutItemCommand } from "@aws-sdk/client-dynamodb";

// Configure DynamoDB
const dynamoDB = new DynamoDBClient({ region: "us-east-2" });

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
        moisture: { S: plant.moisture.S },
        sunlight: { S: plant.sunlight.S },
        temperature: { S: plant.temperature.S },
      },
    };

    await dynamoDB.send(new PutItemCommand(params));
    return NextResponse.json({ message: "Plant added successfully" });
  } catch (error: any) {
    console.error("DynamoDB Add Error:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
