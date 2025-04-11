import { NextResponse } from "next/server";
import { fetchPlantStatus } from "@/app/monitor/fetchPlantStatus"; // adjust the path if needed

export const GET = async () => {
  try {
    const plantStatuses = await fetchPlantStatus();
    return NextResponse.json(plantStatuses, { status: 200 });
  } catch (error: unknown) {
    let errorMessage = "An unknown error occurred";

    if (error instanceof Error) {
      errorMessage = error.message;
    }

    return NextResponse.json({ error: errorMessage }, { status: 500 });
  }
};

/*
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

    return NextResponse.json(plants, { status: 200 });
  } catch (error: unknown) {
    let errorMessage = "An unknown error occurred";

    if (error instanceof Error) {
      errorMessage = error.message;
    }

    return NextResponse.json({ error: errorMessage }, { status: 500 });
  }
}
*/
