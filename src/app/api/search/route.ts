import { NextResponse } from "next/server";
import { DynamoDBClient, QueryCommand } from "@aws-sdk/client-dynamodb";

// Configure DynamoDB
const dynamoDB = new DynamoDBClient({
  region: process.env.AWS_REGION,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
});

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const query = searchParams.get("q");

  if (!query) {
    return NextResponse.json({ error: "Missing search query" }, { status: 400 });
  }

  const params = {
    TableName: "speciesDatabase",
    KeyConditionExpression: "plantName = :name",
    ExpressionAttributeValues: { ":name": { S: query } },
  };

  try {
    const data = await dynamoDB.send(new QueryCommand(params));
    return NextResponse.json(data.Items || []);
  } catch (error) {
    console.error("DynamoDB Query Error:", error); // Print full error details
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}