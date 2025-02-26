import { NextResponse } from "next/server";
import { DynamoDBClient, DeleteItemCommand } from "@aws-sdk/client-dynamodb";

const dynamoDB = new DynamoDBClient({ region: "us-east-2" });

export async function POST(req: Request) {
  try {
    const { plantName } = await req.json(); // Get plant name from request

    if (!plantName) {
      return NextResponse.json({ error: "Plant name is required" }, { status: 400 });
    }

    const params = {
      TableName: "plantData", 
      Key: {
        plantName: { S: plantName }, // Use the correct key structure
      },
    };

    await dynamoDB.send(new DeleteItemCommand(params));

    return NextResponse.json({ message: "Plant removed successfully" });
  } catch (error) {
    console.error("DynamoDB Delete Error:", error);
    return NextResponse.json({ error: "Failed to remove plant" }, { status: 500 });
  }
}
