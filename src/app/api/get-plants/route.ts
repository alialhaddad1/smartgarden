import { NextResponse } from "next/server";
import { DynamoDBClient, ScanCommand } from "@aws-sdk/client-dynamodb";
import { unmarshall } from "@aws-sdk/util-dynamodb";

// DynamoDB configuration
const dynamoDB = new DynamoDBClient({
  region: process.env.AWS_REGION,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
});

export const GET = async () => {
  try {
    const params = { TableName: "plantData" };
    const command = new ScanCommand(params);
    const data = await dynamoDB.send(command);
    const plants = data.Items?.map((item) => unmarshall(item)) ?? [];    
    /*
    const plants = data.Items?.map((item) => ({
      plantName: item.plantName.S,
      moisture: item.moisture.S,
      sunlight: item.sunlight.S,
      temperature: item.temperature.S,
      humidity: item.humidity.S,
      led: item.led.S,
      battery: item.battery.S,
    })) || [];
    */

    return NextResponse.json(plants, { status: 200 });
  } catch (error: unknown) {
    let errorMessage = "An unknown error occurred";

    if (error instanceof Error) {
      errorMessage = error.message;
    }

    return NextResponse.json({ error: errorMessage }, { status: 500 });
  }
}
