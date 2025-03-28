import { NextRequest, NextResponse } from "next/server";
import { DynamoDBClient, UpdateItemCommand } from "@aws-sdk/client-dynamodb";

// Create DynamoDB client
const dynamo = new DynamoDBClient({
  region: "us-east-2", // Change to your AWS region
});

// Handle ESP32 incoming JSON
export async function POST(req: NextRequest) {
  try {
    const { plantName, microMoisture, microSun, microTemp, microHumid, microLED, microBattery } = await req.json();

    // Input validation
    if (!plantName || !microMoisture || !microSun || !microTemp || !microHumid || !microLED || !microBattery) {
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 }
      );
    }

    // Prepare Update Command for DynamoDB
    const params = {
      TableName: "speciesDatabase", // Your DynamoDB table name
      Key: {
        plantName: { S: plantName }, // Primary key
      },
      UpdateExpression:
        "SET microMoisture = :moisture, microSun = :sun, microTemp = :temp, microHumid = :humidity, microLED = :led, microBattery = :battery",
      ExpressionAttributeValues: {
        ":moisture": { S: microMoisture.toString() },
        ":sun": { S: microSun.toString() },
        ":temp": { S: microTemp.toString() },
        ":humid": { S: microHumid.toString() },
        ":led": { S: microLED.toString() },
        ":battery": { S: microBattery.toString() },
      },
    };

    // Send update command to DynamoDB
    const command = new UpdateItemCommand(params);
    await dynamo.send(command);

    return NextResponse.json({ message: "Plant data updated successfully" });
  } catch (error) {
    console.error("Error updating plant data:", error);
    return NextResponse.json(
      { error: "Failed to update plant data" },
      { status: 500 }
    );
  }
}
